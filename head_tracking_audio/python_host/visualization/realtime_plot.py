from queue import Empty
import math
import time

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def _quat_to_euler(qw, qx, qy, qz):
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


def run_realtime_plot(queue, history_len=300, smoothing=0.1):
	roll_hist = []
	pitch_hist = []
	yaw_hist = []
	time_hist = []
	last = None

	fig, ax = plt.subplots()
	line_roll, = ax.plot([], [], label="roll")
	line_pitch, = ax.plot([], [], label="pitch")
	line_yaw, = ax.plot([], [], label="yaw")

	ax.set_title("Orientation (roll, pitch, yaw)")
	ax.set_xlabel("time (s)")
	ax.set_ylabel("degrees")
	ax.set_ylim(-180, 180)
	ax.legend(loc="upper right")

	start_time = time.monotonic()

	def update(_frame):
		nonlocal last
		latest = None

		while True:
			try:
				latest = queue.get_nowait()
			except Empty:
				break

		if latest is None:
			return line_roll, line_pitch, line_yaw

		qw, qx, qy, qz, _timestamp, _host_time = latest
		roll, pitch, yaw = _quat_to_euler(qw, qx, qy, qz)

		if last is None:
			filtered = (roll, pitch, yaw)
		else:
			prev_roll, prev_pitch, prev_yaw = last
			filtered = (
				(1.0 - smoothing) * prev_roll + smoothing * roll,
				(1.0 - smoothing) * prev_pitch + smoothing * pitch,
				(1.0 - smoothing) * prev_yaw + smoothing * yaw,
			)

		last = filtered
		t = time.monotonic() - start_time

		roll_hist.append(filtered[0])
		pitch_hist.append(filtered[1])
		yaw_hist.append(filtered[2])
		time_hist.append(t)

		if len(time_hist) > history_len:
			roll_hist.pop(0)
			pitch_hist.pop(0)
			yaw_hist.pop(0)
			time_hist.pop(0)

		line_roll.set_data(time_hist, roll_hist)
		line_pitch.set_data(time_hist, pitch_hist)
		line_yaw.set_data(time_hist, yaw_hist)

		if time_hist:
			ax.set_xlim(time_hist[0], time_hist[-1] + 0.001)

		return line_roll, line_pitch, line_yaw

	FuncAnimation(fig, update, interval=20, blit=True)
	plt.show()


if __name__ == "__main__":
	from queue import Queue
	from python_host.serial.serial_reader import SerialReader

	q = Queue(maxsize=256)
	reader = SerialReader(q, print_raw=False)
	reader.start()
	run_realtime_plot(q)

