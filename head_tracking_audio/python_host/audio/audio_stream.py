import numpy as np
import sounddevice as sd


class AudioStream:
	def __init__(self, audio_buffer, convolver_ref, sample_rate, block_size, monitor=None):
		self.audio_buffer = audio_buffer
		self.convolver_ref = convolver_ref
		self.sample_rate = int(sample_rate)
		self.block_size = int(block_size)
		self.monitor = monitor
		self.stream = sd.OutputStream(
			channels=2,
			samplerate=self.sample_rate,
			blocksize=self.block_size,
			dtype="float32",
			callback=self._callback,
		)

	def _callback(self, outdata, frames, _time_info, _status):
		if self.monitor is not None:
			self.monitor.start_callback()

		block = self.audio_buffer.get_block(frames)
		convolver = self.convolver_ref.get()

		if convolver is None:
			outdata[:] = 0.0
		else:
			left, right = convolver.process(block)
			outdata[:frames, 0] = left[:frames]
			outdata[:frames, 1] = right[:frames]

		if self.monitor is not None:
			self.monitor.end_callback(frames, self.sample_rate)

	def start(self):
		self.stream.start()

	def stop(self):
		self.stream.stop()

	def close(self):
		self.stream.close()

