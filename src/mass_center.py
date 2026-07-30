import config
import utils


class MassCenter:
	def __init__(self, mass_center_graphic, line_graphic, center_x, center_y, masses):
		self.mass_center_graphic = mass_center_graphic
		self.line_graphic = line_graphic
		self.line = list()
		self.update_pos(center_x, center_y, masses)


	def update_pos(self, centers_x, centers_y, masses):
		x, y = 0, 0
		for i in range(len(centers_x)):
			x += masses[i] * centers_x[i]
			y += masses[i] * centers_y[i]
		x /= sum(masses)
		y /= sum(masses)

		self.pos = (x, y)
		self.line.append(self.pos)

	def update_graphic(self, cx, cy, w, h, scale):
		widget_coords = utils.coords2window(self.pos[0], self.pos[1], cx, cy, w, h, scale)
		self.mass_center_graphic.pos = (widget_coords[0] - config.MASS_CENTER_SIZE/2, widget_coords[1] - config.MASS_CENTER_SIZE/2)
		self.line_graphic.points += widget_coords

	def update_size(self, cx, cy, w, h, scale):
		widget_coords = utils.coords2window(self.pos[0], self.pos[1], cx, cy, w, h, scale)
		self.mass_center_graphic.pos = (widget_coords[0] - config.MASS_CENTER_SIZE/2, widget_coords[1] - config.MASS_CENTER_SIZE/2)
		
		size = min(w, h)
		for i in range(len(self.line_graphic.points)):
			if i % 2 == 0:
				self.line_graphic.points[i] = utils.coord2window(self.line[i//2][0], cx, size, scale)
			else:
				self.line_graphic.points[i] = utils.coord2window(self.line[i//2][1], cy, size, scale)
