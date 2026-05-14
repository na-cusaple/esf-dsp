import argparse
from queue import Queue

from python_host.serial.serial_reader import SerialReader
from python_host.visualization.realtime_plot import run_realtime_plot
from python_host.visualization.imu_viewer import run_imu_viewer


def main():
	parser = argparse.ArgumentParser(description="Head tracking visualization")
	parser.add_argument("--port", default=None, help="Serial port, e.g. /dev/tty.usbmodemXXXX or COM3")
	parser.add_argument("--baud", type=int, default=460800)
	parser.add_argument("--mode", choices=["plot", "cube", "print"], default="plot")
	parser.add_argument("--history", type=int, default=300)
	parser.add_argument("--smoothing", type=float, default=0.1)
	parser.add_argument("--timeout", type=float, default=1.0)
	parser.add_argument("--print-raw", action="store_true")
	args = parser.parse_args()

	queue = Queue(maxsize=256)
	reader = SerialReader(
		queue,
		port=args.port,
		baud=args.baud,
		timeout=args.timeout,
		print_raw=args.print_raw or args.mode == "print",
	)
	reader.start()

	try:
		if args.mode == "plot":
			run_realtime_plot(queue, history_len=args.history, smoothing=args.smoothing)
		elif args.mode == "cube":
			run_imu_viewer(queue, fps=60, smoothing=args.smoothing)
		else:
			import time
			while True:
				time.sleep(1.0)
	finally:
		reader.stop()


if __name__ == "__main__":
	main()

