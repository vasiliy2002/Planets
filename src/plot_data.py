import numpy as np

class PlotData():
	def __init__(self, max_years_range=20):
		self.data = list()
		self.max_years_range = max_years_range

	def add(self, t, dist):
		if len(self.data) == 0:
			self.data.append((t, dist))
		elif t.tt > self.data[-1][0].tt:
			while len(self.data) > 0 and t.tt - self.data[0][0].tt > self.max_years_range * 365:
				self.data.pop(0)
			self.data.append((t, dist))
		elif t.tt < self.data[0][0].tt:
			while len(self.data) > 0 and self.data[-1][0].tt - t.tt > self.max_years_range * 365:
				self.data.pop(-1)
			self.data.insert(0, (t, dist))

	def get_times(self):
		return np.array([x[0] for x in self.data])

	def get_dists(self):
		return np.array([x[1] for x in self.data])

	def clear(self):
		self.data = list()
