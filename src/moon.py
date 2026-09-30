from skyfield.api import load
import math
import utils
from scipy import optimize



def degrees(x):
	x = x % (2*math.pi)
	return (x * 180 / math.pi) % 360

def radians(x):
	x = x % 360
	return (x * math.pi / 180)

class Moon():
	def __init__(self):
		self.i = radians(5.1454)
		self.a = 60.2666
		self.e = 0.054900

		self.N = None
		self.w = None
		self.M = None

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

	def get_pos(self, date):
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
		r = math.sqrt(xeclip**2 + yeclip**2) * 6371

		return r, degrees(longt)

ts = load.timescale()
time = ts.tt(2000, 1, 1)
moon = Moon()

r, v = moon.get_pos(time)
print(r, v)

