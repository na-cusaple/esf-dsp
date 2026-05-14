import argparse
import math
import threading
import time
from queue import Queue, Empty

from python_host.serial.serial_reader import SerialReader
from python_host.dsp.hrtf_loader import load_cipic_mat
from python_host.dsp.hrtf_selector import select_hrir, select_hrir_interpolated
from python_host.audio.buffer_manager import AudioFileBuffer, OverlapAddConvolver
from python_host.audio.audio_stream import AudioStream
from python_host.audio.latency_monitor import LatencyMonitor
from python_host.config.audio_config import (
    AUDIO_SAMPLE_RATE,
    BLOCK_SIZE,
    QUEUE_SIZE,
    HRTF_UPDATE_HZ,
    QUAT_SMOOTHING,
    HRTF_INTERPOLATE,
    HRTF_INTERP_STEP,
)


def _normalize_quat(q):
    qw, qx, qy, qz = q
    norm = math.sqrt(qw * qw + qx * qx + qy * qy + qz * qz)
    if norm <= 0.0:
        return 1.0, 0.0, 0.0, 0.0
    return qw / norm, qx / norm, qy / norm, qz / norm


def _quat_to_euler(q):
    qw, qx, qy, qz = _normalize_quat(q)

    sinr_cosp = 2.0 * (qw * qx + qy * qz)
    cosr_cosp = 1.0 - 2.0 * (qx * qx + qy * qy)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    sinp = 2.0 * (qw * qy - qz * qx)
    if abs(sinp) >= 1.0:
        pitch = math.copysign(math.pi / 2.0, sinp)
    else:
        pitch = math.asin(sinp)

    siny_cosp = 2.0 * (qw * qz + qx * qy)
    cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    return math.degrees(roll), math.degrees(pitch), math.degrees(yaw)


def _smooth_quat(prev, curr, alpha):
    qw = (1.0 - alpha) * prev[0] + alpha * curr[0]
    qx = (1.0 - alpha) * prev[1] + alpha * curr[1]
    qy = (1.0 - alpha) * prev[2] + alpha * curr[2]
    qz = (1.0 - alpha) * prev[3] + alpha * curr[3]
    return _normalize_quat((qw, qx, qy, qz))


class ConvolverRef:
    def __init__(self):
        self._convolver = None

    def get(self):
        return self._convolver

    def set(self, convolver):
        self._convolver = convolver


class OrientationState:
    def __init__(self):
        self.latest = (1.0, 0.0, 0.0, 0.0)
        self.timestamp = 0.0

    def update(self, quat, timestamp):
        self.latest = quat
        self.timestamp = timestamp

    def get(self):
        return self.latest, self.timestamp


class HrtfUpdater:
    def __init__(self, dataset, convolver_ref, block_size, interpolate=False, interp_step=0.1):
        self.dataset = dataset
        self.convolver_ref = convolver_ref
        self.block_size = block_size
        self.interpolate = interpolate
        self.interp_step = interp_step
        self.current_key = None

    def _make_key(self, used, alpha):
        if not self.interpolate:
            return used

        if self.interp_step <= 0.0:
            return used + (round(alpha, 3),)

        alpha_bin = round(alpha / self.interp_step) * self.interp_step
        return used + (alpha_bin,)

    def update_from_quat(self, quat):
        _roll, pitch, yaw = _quat_to_euler(quat)
        if self.interpolate:
            hrir_l, hrir_r, used, alpha = select_hrir_interpolated(self.dataset, yaw, pitch)
            key = self._make_key(used, alpha)
        else:
            hrir_l, hrir_r, used = select_hrir(self.dataset, yaw, pitch)
            key = self._make_key(used, 0.0)

        if key != self.current_key:
            convolver = OverlapAddConvolver(hrir_l, hrir_r, self.block_size)
            self.convolver_ref.set(convolver)
            self.current_key = key


class OrientationWorker(threading.Thread):
    def __init__(self, queue, state, hrtf_updater, smoothing=0.1, update_hz=50, monitor=None):
        super().__init__(daemon=True)
        self.queue = queue
        self.state = state
        self.hrtf_updater = hrtf_updater
        self.smoothing = smoothing
        self.update_period = 1.0 / float(update_hz) if update_hz > 0 else 0.02
        self.monitor = monitor
        self._stop_event = threading.Event()
        self._last_quat = (1.0, 0.0, 0.0, 0.0)

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            updated = False
            while True:
                try:
                    qw, qx, qy, qz, timestamp, host_time = self.queue.get_nowait()
                except Empty:
                    break

                curr = _normalize_quat((qw, qx, qy, qz))
                self._last_quat = _smooth_quat(self._last_quat, curr, self.smoothing)
                self.state.update(self._last_quat, timestamp)
                if self.monitor is not None:
                    self.monitor.record_queue_age(time.perf_counter() - host_time)
                updated = True

            if updated:
                self.hrtf_updater.update_from_quat(self._last_quat)

            time.sleep(self.update_period)


def run_realtime_spatializer(args):
    audio_buffer = AudioFileBuffer.from_wav(args.input, target_sample_rate=args.sample_rate)
    sample_rate = audio_buffer.sample_rate

    dataset = load_cipic_mat(args.hrtf)

    convolver_ref = ConvolverRef()
    hrtf_updater = HrtfUpdater(
        dataset,
        convolver_ref,
        args.block_size,
        interpolate=args.interpolate,
        interp_step=args.interp_step,
    )
    hrtf_updater.update_from_quat((1.0, 0.0, 0.0, 0.0))

    orientation_queue = Queue(maxsize=args.queue_size)
    monitor = LatencyMonitor()
    serial_reader = SerialReader(
        orientation_queue,
        port=args.port,
        baud=args.baud,
        timeout=args.timeout,
        print_raw=False,
        monitor=monitor,
    )

    state = OrientationState()
    worker = OrientationWorker(
        orientation_queue,
        state,
        hrtf_updater,
        smoothing=args.smoothing,
        update_hz=args.hrtf_update_hz,
        monitor=monitor,
    )
    stream = AudioStream(audio_buffer, convolver_ref, sample_rate, args.block_size, monitor)

    serial_reader.start()
    worker.start()
    stream.start()

    try:
        while True:
            time.sleep(1.0)
            if args.print_stats:
                stats = monitor.stats()
                if stats:
                    parts = []
                    if "avg_ms" in stats:
                        parts.append(
                            "callback avg %.2f ms max %.2f ms budget %.2f ms overruns %d"
                            % (stats["avg_ms"], stats["max_ms"], stats["budget_ms"], stats["overruns"])
                        )
                    if "queue_age_avg_ms" in stats:
                        parts.append(
                            "queue age avg %.2f ms max %.2f ms"
                            % (stats["queue_age_avg_ms"], stats["queue_age_max_ms"])
                        )
                    if "uart_delay_avg_ms" in stats:
                        parts.append(
                            "uart delay avg %.2f ms max %.2f ms"
                            % (stats["uart_delay_avg_ms"], stats["uart_delay_max_ms"])
                        )
                    print(" | ".join(parts))
    except KeyboardInterrupt:
        pass
    finally:
        stream.stop()
        stream.close()
        serial_reader.stop()
        worker.stop()


def main():
    parser = argparse.ArgumentParser(description="Realtime spatial audio")
    parser.add_argument("--input", required=True, help="Input mono wav")
    parser.add_argument("--hrtf", required=True, help="CIPIC .mat file path")
    parser.add_argument("--port", default=None, help="Serial port, e.g. /dev/tty.usbmodemXXXX or COM3")
    parser.add_argument("--baud", type=int, default=460800)
    parser.add_argument("--timeout", type=float, default=1.0)
    parser.add_argument("--block-size", type=int, default=BLOCK_SIZE)
    parser.add_argument("--queue-size", type=int, default=QUEUE_SIZE)
    parser.add_argument("--sample-rate", type=int, default=None)
    parser.add_argument("--smoothing", type=float, default=QUAT_SMOOTHING)
    parser.add_argument("--hrtf-update-hz", type=int, default=HRTF_UPDATE_HZ)
    parser.add_argument("--interpolate", action="store_true", default=HRTF_INTERPOLATE)
    parser.add_argument("--interp-step", type=float, default=HRTF_INTERP_STEP)
    parser.add_argument("--print-stats", action="store_true")
    args = parser.parse_args()

    run_realtime_spatializer(args)


if __name__ == "__main__":
    main()
