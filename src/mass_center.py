import config

class MassCenter:
	def __init__(self, mass_center_graphic, line_graphic, center_x, center_y, masses):
		self.mass_center_graphic = mass_center_graphic
		self.line_graphic = line_graphic
		self.center = self.count_center(center_x, center_y, masses)
		self.line = list()

	def count_center(self, centers_x, centers_y, masses):
		x, y = 0, 0
		for i in range(len(centers_x)):
			x += masses[i] * centers_x[i]
			y += masses[i] * centers_y[i]
		x /= sum(masses)
		y /= sum(masses)
		return x, y

	def update(self, centers_x, centers_y, masses, cx, cy, w, h, scale):
		size = min(w, h)
		self.center = self.count_center(centers_x, centers_y, masses)
		self.mass_center_graphic.pos = (int(cx + self.center[0] * (size/2) * scale - config.MASS_CENTER_SIZE/2), int(cy + self.center[1] * (size/2) * scale - config.MASS_CENTER_SIZE/2))
		self.line_graphic.points += [self.mass_center_graphic.pos[0] + config.MASS_CENTER_SIZE/2, self.mass_center_graphic.pos[1] + config.MASS_CENTER_SIZE/2]
		self.line.append(self.center)


	def update_trajectory(self, cx, cy, w, h, scale):
		size = min(w, h)
		for i in range(len(self.line_graphic.points)):
			if i % 2 == 0:
				self.line_graphic.points[i] = cx + self.line[i//2][0] * (size/2) * scale
			else:
				self.line_graphic.points[i] = cy + self.line[i//2][1] * (size/2) * scale
