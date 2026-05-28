from dataclasses import dataclass
import math
from typing import Optional

import numpy as np
import scipy.io
from scipy.signal import resample_poly


@dataclass
class HrtfDataset:
	hrir_l: np.ndarray
	hrir_r: np.ndarray
	azimuths: np.ndarray
	elevations: np.ndarray
	sample_rate: Optional[int] = None


def _extract_sample_rate(data):
	for key in ("fs", "Fs", "sampling_rate", "sample_rate"):
		value = data.get(key)
		if value is None:
			continue
		try:
			arr = np.asarray(value).reshape(-1)
			if arr.size > 0:
				return int(arr[0])
		except (TypeError, ValueError):
			continue
	return None


def _resample_hrir(hrir, src_rate, dst_rate):
	if src_rate == dst_rate:
		return hrir

	g = math.gcd(int(src_rate), int(dst_rate))
	up = int(dst_rate // g)
	down = int(src_rate // g)
	return resample_poly(hrir, up, down, axis=-1).astype(np.float32)


def load_cipic_mat(mat_path, target_sample_rate=None, source_sample_rate=None):
	data = scipy.io.loadmat(mat_path)

	hrir_l = data.get("hrir_l")
	hrir_r = data.get("hrir_r")
	azim = data.get("azim_v")
	elev = data.get("elev_v")

	if hrir_l is None or hrir_r is None or azim is None or elev is None:
		# allow MAT files that contain HRIR arrays but not azimuth/elevation vectors
		if hrir_l is None or hrir_r is None:
			raise ValueError("Missing CIPIC keys: hrir_l/hrir_r/azim_v/elev_v")
		# infer azimuth/elevation indices from HRIR shape
		shp = np.shape(hrir_l)
		if len(shp) >= 3:
			n1, n2 = int(shp[0]), int(shp[1])
		elif len(shp) == 2:
			n1, n2 = int(shp[0]), 1
		else:
			n1, n2 = 1, 1
		azim = np.arange(n2)
		elev = np.arange(n1)

	azim = np.array(azim).reshape(-1)
	elev = np.array(elev).reshape(-1)

	sample_rate = _extract_sample_rate(data)
	if sample_rate is None and source_sample_rate is not None:
		sample_rate = int(source_sample_rate)

	if target_sample_rate is not None and sample_rate is not None:
		target_sample_rate = int(target_sample_rate)
		if target_sample_rate != int(sample_rate):
			hrir_l = _resample_hrir(hrir_l, sample_rate, target_sample_rate)
			hrir_r = _resample_hrir(hrir_r, sample_rate, target_sample_rate)
			sample_rate = target_sample_rate

	return HrtfDataset(
		hrir_l=hrir_l,
		hrir_r=hrir_r,
		azimuths=azim,
		elevations=elev,
		sample_rate=sample_rate,
	)

