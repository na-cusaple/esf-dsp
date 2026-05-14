from dataclasses import dataclass

import numpy as np
import scipy.io


@dataclass
class HrtfDataset:
	hrir_l: np.ndarray
	hrir_r: np.ndarray
	azimuths: np.ndarray
	elevations: np.ndarray


def load_cipic_mat(mat_path):
	data = scipy.io.loadmat(mat_path)

	hrir_l = data.get("hrir_l")
	hrir_r = data.get("hrir_r")
	azim = data.get("azim_v")
	elev = data.get("elev_v")

	if hrir_l is None or hrir_r is None or azim is None or elev is None:
		raise ValueError("Missing CIPIC keys: hrir_l/hrir_r/azim_v/elev_v")

	azim = np.array(azim).reshape(-1)
	elev = np.array(elev).reshape(-1)

	return HrtfDataset(hrir_l=hrir_l, hrir_r=hrir_r, azimuths=azim, elevations=elev)

