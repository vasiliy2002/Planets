def get_centers_and_masses(planets):
	center_x, center_y = list(), list()
	mass = list()

	for planet in planets:
		center = planet.get_center()
		center_x.append(center[0])
		center_y.append(center[1])
		mass.append(planet.mass)

	return center_x, center_y, mass

