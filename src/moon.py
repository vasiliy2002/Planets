from skyfield.api import load
import math
import utils
from scipy import optimize
import configs.config as config


def degrees(x):
	x = x % (2*math.pi)
	return (x * 180 / math.pi) % 360

def radians(x):
	x = x % 360
	return (x * math.pi / 180)

class Moon():
	def __init__(self, orbit_graphic, planet_graphic, rotation_graphic):
		self.i = radians(5.1454)
		self.a = 60.2666 * 6371
		self.e = 0.054900
		self.c = self.a * self.e
		self.b = self.a * math.sqrt(1 - self.e ** 2)
		
		self.N = None
		self.w = None
		self.M = None

		self.orbit_graphic = orbit_graphic
		self.planet_graphic = planet_graphic
		self.rotation_graphic = rotation_graphic

		self.origin = (0, 0)
		self.polar_coords = (1, 1)

	def date2d(self, date):
		ut1 = date.ut1_calendar()
		y = ut1[0]
		m = ut1[1]
		D = ut1[2]
		UT = ut1[3] + ut1[4] / 60 + ut1[5] / 3600

		d = 367*y - 7 * ( y + (m+9)//12 ) // 4 - 3 * ( ( y + (m-9)//7 ) // 100 + 1 ) // 4 + 275*m//9 + D - 730515
		d = d + UT / 24.

		return d

	def set_primary_orbital_elements(self, d):
		self.N = radians(125.1228 - 0.0529538083 * d)
		self.w = radians(318.0634 + 0.1643573223 * d)
		self.M = radians(115.3654 + 13.0649929509 * d)
	
	def print_params(self):
		print("Params:")
		print(degrees(self.N))
		print(degrees(self.i))
		print(degrees(self.w))
		print(self.a)
		print(self.e)
		print(degrees(self.M))
		print("----------")

	def update_pos(self, date):
		d = self.date2d(date)
		self.set_primary_orbital_elements(d)

		E0 = self.M if self.e <= 0.8 else math.pi
		E = optimize.newton(lambda x: utils.kepler_eq(x, self.M, self.e), E0)

		xv = self.a * ( math.cos(E) - self.e )
		yv = self.a * ( math.sqrt(1.0 - self.e*self.e) * math.sin(E) )

		v = math.atan2( yv, xv )
		r = math.sqrt( xv*xv + yv*yv )

		xeclip = r * ( math.cos(self.N) * math.cos(v+self.w) - math.sin(self.N) * math.sin(v+self.w) * math.cos(self.i) )
		yeclip = r * ( math.sin(self.N) * math.cos(v+self.w) + math.cos(self.N) * math.sin(v+self.w) * math.cos(self.i) )
		zeclip = r * math.sin(v+self.w) * math.sin(self.i)

		longt = math.atan2(yeclip, xeclip)
		lat = math.atan2(zeclip, math.sqrt( xeclip*xeclip + yeclip*yeclip ))
		r = math.sqrt(xeclip**2 + yeclip**2) #* 6371

		self.polar_coords = (r, longt)

	def get_xy(self):
		r, phi = self.polar_coords
		x, y = r * math.cos(phi) * 50, r * math.sin(phi) * 50
		return self.origin[0] + x, self.origin[1] + y

	def update_planet_graphic(self, cx, cy, w, h, scale):
		x, y = self.get_xy()
		widget_coords = utils.coords2window(x, y, cx, cy, w, h, scale)
		self.planet_graphic.pos = (widget_coords[0] - config.PLANET_SIZE/2, widget_coords[1] - config.PLANET_SIZE/2)

	def update_orbit_graphic(self, cx, cy, w, h, scale):
		x, y = self.origin
		origin_coords = utils.coords2window(x, y, cx, cy, w, h, scale)

		self.rotation_graphic.origin = origin_coords
		self.rotation_graphic.angle = degrees(self.N + self.w)
		self.orbit_graphic.ellipse = (origin_coords[0] - self.c*scale*50 - self.a*scale*50, origin_coords[1] - self.b*scale*50, 2*self.a*scale*50, 2*self.b*scale*50)

	def update_graphic(self, cx, cy, w, h, scale):
		self.update_planet_graphic(cx, cy, w, h, scale)
		self.update_orbit_graphic(cx, cy, w, h, scale)

