def parse_quaternion(line):
	if not line:
		return None

	parts = line.split(",")
	if len(parts) < 5:
		return None

	try:
		qw = float(parts[0])
		qx = float(parts[1])
		qy = float(parts[2])
		qz = float(parts[3])
		timestamp = float(parts[4])
	except (ValueError, IndexError):
		return None

	return qw, qx, qy, qz, timestamp

