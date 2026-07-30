def get_centers_and_masses(planets):
	center_x, center_y = list(), list()
	mass = list()

	for planet in planets:
		center = planet.get_xy()
		center_x.append(center[0])
		center_y.append(center[1])
		mass.append(planet.mass)

	return center_x, center_y, mass

def coord2window(pos, c, size, scale):
	return c + pos * (size/2) * scale

def coords2window(pos_x, pos_y, cx, cy, w, h, scale):
	size = min(w, h)		
	return (int(cx + pos_x * (size/2) * scale), int(cy + pos_y * (size/2) * scale))




