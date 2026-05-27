import argparse

import numpy as np
import soundfile as sf

from .convolution import fft_convolve_mono_to_stereo, normalize_audio
from .hrtf_loader import load_cipic_mat
from .hrtf_selector import select_hrir
from python_host.config.audio_config import HRTF_SAMPLE_RATE


def _to_mono(audio):
	if audio.ndim == 1:
		return audio
	if audio.ndim == 2:
		return audio.mean(axis=1)
	raise ValueError("Unsupported audio shape")


def spatialize_file(
	input_wav,
	output_wav,
	hrtf_mat,
	yaw_deg,
	pitch_deg=0.0,
	normalize=True,
	hrtf_sample_rate=None,
):
	audio, sr = sf.read(input_wav)
	audio = _to_mono(audio)

	dataset = load_cipic_mat(
		hrtf_mat,
		target_sample_rate=sr,
		source_sample_rate=hrtf_sample_rate,
	)
	hrir_l, hrir_r, used_angles = select_hrir(dataset, yaw_deg, pitch_deg)

	left, right = fft_convolve_mono_to_stereo(audio, hrir_l, hrir_r)
	stereo = np.column_stack((left, right))

	if normalize:
		stereo = normalize_audio(stereo)

	sf.write(output_wav, stereo, sr)
	return used_angles


def main():
	parser = argparse.ArgumentParser(description="Offline HRTF spatializer")
	parser.add_argument("--input", required=True, help="Input mono wav")
	parser.add_argument("--output", required=True, help="Output stereo wav")
	parser.add_argument("--hrtf", required=True, help="CIPIC .mat file path")
	parser.add_argument("--yaw", type=float, default=-90.0)
	parser.add_argument("--pitch", type=float, default=0.0)
	parser.add_argument("--hrtf-sr", type=int, default=HRTF_SAMPLE_RATE)
	parser.add_argument("--no-normalize", action="store_true")
	args = parser.parse_args()

	used = spatialize_file(
		args.input,
		args.output,
		args.hrtf,
		args.yaw,
		pitch_deg=args.pitch,
		normalize=not args.no_normalize,
		hrtf_sample_rate=args.hrtf_sr,
	)
	print("HRTF used (azimuth, elevation):", used)


if __name__ == "__main__":
	main()

