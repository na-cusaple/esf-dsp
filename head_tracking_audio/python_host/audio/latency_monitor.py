import time
from collections import deque


class LatencyMonitor:
	def __init__(self, window=200):
		self.window = int(window)
		self.samples = deque(maxlen=self.window)
		self.queue_age_samples = deque(maxlen=self.window)
		self.uart_delay_samples = deque(maxlen=self.window)
		self._start = None

	def start_callback(self):
		self._start = time.perf_counter()

	def end_callback(self, frames, sample_rate):
		if self._start is None:
			return

		elapsed = time.perf_counter() - self._start
		budget = float(frames) / float(sample_rate) if sample_rate > 0 else 0.0
		self.samples.append((elapsed, budget))
		self._start = None

	def record_queue_age(self, age_sec):
		if age_sec is None:
			return
		self.queue_age_samples.append(float(age_sec))

	def record_uart_delay(self, delay_sec):
		if delay_sec is None:
			return
		self.uart_delay_samples.append(float(delay_sec))

	def stats(self):
		if not self.samples and not self.queue_age_samples and not self.uart_delay_samples:
			return None

		stats = {}
		if self.samples:
			elapsed = [s[0] for s in self.samples]
			budget = [s[1] for s in self.samples]
			stats["avg_ms"] = 1000.0 * (sum(elapsed) / len(elapsed))
			stats["max_ms"] = 1000.0 * max(elapsed)
			stats["overruns"] = sum(1 for e, b in self.samples if b > 0.0 and e > b)
			stats["budget_ms"] = 1000.0 * (sum(budget) / len(budget)) if budget else 0.0

		if self.queue_age_samples:
			stats["queue_age_avg_ms"] = 1000.0 * (sum(self.queue_age_samples) / len(self.queue_age_samples))
			stats["queue_age_max_ms"] = 1000.0 * max(self.queue_age_samples)

		if self.uart_delay_samples:
			stats["uart_delay_avg_ms"] = 1000.0 * (sum(self.uart_delay_samples) / len(self.uart_delay_samples))
			stats["uart_delay_max_ms"] = 1000.0 * max(self.uart_delay_samples)

		return stats

