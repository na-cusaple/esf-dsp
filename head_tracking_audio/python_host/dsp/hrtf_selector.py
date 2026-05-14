import numpy as np


def _nearest_index(values, target):
	values = np.asarray(values).reshape(-1)
	if values.size == 0:
		raise ValueError("Empty angle array")
	return int(np.argmin(np.abs(values - target)))


def _get_hrir_at(dataset, az_idx, el_idx):
	hrir_l = dataset.hrir_l
	hrir_r = dataset.hrir_r

	if hrir_l.ndim != 3:
		raise ValueError("Expected 3D HRIR arrays")

	if hrir_l.shape[0] == dataset.elevations.size and hrir_l.shape[1] == dataset.azimuths.size:
		left = hrir_l[el_idx, az_idx, :]
		right = hrir_r[el_idx, az_idx, :]
	elif hrir_l.shape[0] == dataset.azimuths.size and hrir_l.shape[1] == dataset.elevations.size:
		left = hrir_l[az_idx, el_idx, :]
		right = hrir_r[az_idx, el_idx, :]
	else:
		raise ValueError("HRIR shape does not match azimuth/elevation vectors")

	return left, right


def select_hrir(dataset, yaw_deg, pitch_deg=0.0):
	az_idx = _nearest_index(dataset.azimuths, yaw_deg)
	el_idx = _nearest_index(dataset.elevations, pitch_deg)

	left, right = _get_hrir_at(dataset, az_idx, el_idx)
	used = (float(dataset.azimuths[az_idx]), float(dataset.elevations[el_idx]))
	return left, right, used


def select_hrir_interpolated(dataset, yaw_deg, pitch_deg=0.0):
	az = np.asarray(dataset.azimuths).reshape(-1)
	order = np.argsort(az)
	az_sorted = az[order]

	if az_sorted.size == 0:
		raise ValueError("Empty azimuth array")

	if yaw_deg <= az_sorted[0]:
		idx0 = idx1 = order[0]
		alpha = 0.0
	elif yaw_deg >= az_sorted[-1]:
		idx0 = idx1 = order[-1]
		alpha = 0.0
	else:
		insert = int(np.searchsorted(az_sorted, yaw_deg))
		idx0 = order[insert - 1]
		idx1 = order[insert]
		az0 = float(az_sorted[insert - 1])
		az1 = float(az_sorted[insert])
		alpha = 0.0 if az1 == az0 else (yaw_deg - az0) / (az1 - az0)

	el_idx = _nearest_index(dataset.elevations, pitch_deg)
	left0, right0 = _get_hrir_at(dataset, idx0, el_idx)
	left1, right1 = _get_hrir_at(dataset, idx1, el_idx)

	left = (1.0 - alpha) * left0 + alpha * left1
	right = (1.0 - alpha) * right0 + alpha * right1

	used = (float(dataset.azimuths[idx0]), float(dataset.azimuths[idx1]), float(dataset.elevations[el_idx]))
	return left, right, used, float(alpha)

