import numpy as np
from scipy.signal import fftconvolve


def fft_convolve_mono_to_stereo(audio, hrir_l, hrir_r):
	if audio.ndim != 1:
		raise ValueError("Audio must be mono (1D)")

	left = fftconvolve(audio, hrir_l, mode="full")
	right = fftconvolve(audio, hrir_r, mode="full")
	return left, right


def normalize_audio(signal):
	peak = np.max(np.abs(signal))
	if peak <= 0.0:
		return signal
	return signal / peak

