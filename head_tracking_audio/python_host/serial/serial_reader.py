import threading
import time
from queue import Empty, Full

import serial
from serial.tools import list_ports

from .parser import parse_quaternion


def find_default_port():
	ports = list_ports.comports()
	if not ports:
		return None

	preferred = ["usbmodem", "ttyACM", "ttyUSB", "COM"]
	for key in preferred:
		for port in ports:
			if key in port.device:
				return port.device

	return ports[0].device


class SerialReader(threading.Thread):
	def __init__(self, queue, port=None, baud=460800, timeout=1.0, print_raw=False, monitor=None):
		super().__init__(daemon=True)
		self.queue = queue
		self.port = port
		self.baud = baud
		self.timeout = timeout
		self.print_raw = print_raw
		self.monitor = monitor
		self._stop_event = threading.Event()
		self._ser = None
		self._time_offset = None

	def open(self):
		if self.port is None:
			self.port = find_default_port()
		if self.port is None:
			raise serial.SerialException("No serial port detected")
		self._ser = serial.Serial(port=self.port, baudrate=self.baud, timeout=self.timeout)

	def close(self):
		if self._ser is not None:
			try:
				self._ser.close()
			finally:
				self._ser = None

	def stop(self):
		self._stop_event.set()
		self.close()

	def _push_latest(self, data):
		try:
			self.queue.put_nowait(data)
		except Full:
			try:
				self.queue.get_nowait()
			except Empty:
				pass
			try:
				self.queue.put_nowait(data)
			except Full:
				pass

	def run(self):
		while not self._stop_event.is_set():
			if self._ser is None:
				try:
					self.open()
				except serial.SerialException:
					time.sleep(0.5)
					continue

			try:
				line = self._ser.readline().decode(errors="ignore").strip()
			except serial.SerialException:
				self.close()
				time.sleep(0.5)
				continue

			if not line:
				continue

			if self.print_raw:
				print(line)

			data = parse_quaternion(line)
			if data is not None:
				qw, qx, qy, qz, timestamp = data
				host_time = time.perf_counter()
				if self.monitor is not None:
					device_time = float(timestamp) / 1000.0
					if self._time_offset is None:
						self._time_offset = host_time - device_time
					else:
						self._time_offset = 0.99 * self._time_offset + 0.01 * (host_time - device_time)
					uart_delay = host_time - (device_time + self._time_offset)
					self.monitor.record_uart_delay(uart_delay)
				self._push_latest((qw, qx, qy, qz, timestamp, host_time))

