import math

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly


def _next_pow_two(value):
	if value <= 0:
		return 1
	return 1 << (value - 1).bit_length()


class AudioFileBuffer:
	def __init__(self, audio, sample_rate):
		self.audio = np.asarray(audio, dtype=np.float32)
		self.sample_rate = int(sample_rate)
		self.position = 0
		self.length = int(self.audio.shape[0])

	@classmethod
	def from_wav(cls, path, target_sample_rate=None):
		audio, sr = sf.read(path, dtype="float32")
		if audio.ndim == 2:
			audio = audio.mean(axis=1)

		if target_sample_rate is not None:
			new_sr = int(target_sample_rate)
			if new_sr != int(sr):
				audio = _resample_audio(audio, int(sr), new_sr)
				sr = new_sr

		return cls(audio, sr)


def _resample_audio(audio, src_rate, dst_rate):
	if src_rate == dst_rate:
		return audio

	g = math.gcd(int(src_rate), int(dst_rate))
	up = int(dst_rate // g)
	down = int(src_rate // g)
	return resample_poly(audio, up, down).astype(np.float32)

	def get_block(self, frames):
		if frames <= 0 or self.length == 0:
			return np.zeros((frames,), dtype=np.float32)

		end = self.position + frames
		if end <= self.length:
			block = self.audio[self.position:end]
			self.position = end if end < self.length else 0
			return block

		tail = self.audio[self.position:self.length]
		head = self.audio[0:end - self.length]
		self.position = end - self.length
		return np.concatenate((tail, head))


class OverlapAddConvolver:
	def __init__(self, hrir_l, hrir_r, block_size):
		self.block_size = int(block_size)
		self.hrir_l = np.asarray(hrir_l, dtype=np.float32)
		self.hrir_r = np.asarray(hrir_r, dtype=np.float32)

		fft_size = _next_pow_two(self.block_size + self.hrir_l.size - 1)
		self.fft_size = int(fft_size)

		self.hrir_l_fft = np.fft.rfft(self.hrir_l, self.fft_size)
		self.hrir_r_fft = np.fft.rfft(self.hrir_r, self.fft_size)

		overlap_len = self.fft_size - self.block_size
		self.overlap_l = np.zeros((overlap_len,), dtype=np.float32)
		self.overlap_r = np.zeros((overlap_len,), dtype=np.float32)

	def process(self, block):
		block = np.asarray(block, dtype=np.float32)
		if block.size != self.block_size:
			padded = np.zeros((self.block_size,), dtype=np.float32)
			count = min(block.size, self.block_size)
			padded[:count] = block[:count]
			block = padded

		fft_in = np.zeros((self.fft_size,), dtype=np.float32)
		fft_in[:self.block_size] = block

		x_fft = np.fft.rfft(fft_in)
		y_l = np.fft.irfft(x_fft * self.hrir_l_fft, self.fft_size)
		y_r = np.fft.irfft(x_fft * self.hrir_r_fft, self.fft_size)

		out_l = y_l[:self.block_size].copy()
		out_r = y_r[:self.block_size].copy()

		overlap_len = self.overlap_l.size
		add_len = min(overlap_len, self.block_size)
		if add_len > 0:
			out_l[:add_len] += self.overlap_l[:add_len]
			out_r[:add_len] += self.overlap_r[:add_len]

		self.overlap_l = y_l[self.block_size:self.block_size + overlap_len]
		self.overlap_r = y_r[self.block_size:self.block_size + overlap_len]

		return out_l, out_r

