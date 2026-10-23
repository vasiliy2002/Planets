from skyfield.api import load
import math
import utils
from scipy import optimize
import configs.config as config
from skyfield.api import load

ts = load.timescale()

def degrees(x):
    x = x % (2*math.pi)
    return (x * 180 / math.pi) % 360

def radians(x):
    x = x % 360
    return (x * math.pi / 180)

class MoonPosition():
    def __init__(self, earth_pos, origin):
        self.i = radians(5.1454)
        self.a = 60.2666 * 6371
        self.e = 0.054900
        self.c = self.a * self.e
        self.b = self.a * math.sqrt(1 - self.e ** 2)
        
        self.N = None
        self.w = None
        self.M = None
        self.additional_scale = 50

        self.earth_pos = earth_pos
        self.polar_coords = (1, 1)

        self.origin = origin
        self.orbit_changed = True

        self.start_angle = 0

    def last_t(self):
        return self.line[-1][2]

    def get_xy(self):
        r, phi = self.polar_coords
        x, y = r * math.cos(phi) * self.additional_scale, r * math.sin(phi) * self.additional_scale
        earth_x, earth_y = self.earth_pos.get_xy()
        return earth_x + x, earth_y + y

    def get_polar_coords(self):
        pass

    def get_origin_coords(self):
        if not self.origin:
            return 0, 0
        else:
            x, y = self.get_xy()
            ox, oy = self.origin.get_xy()
            return x - ox, y - oy

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

    def update_pos(self, date):
        d = self.date2d(date)
        self.set_primary_orbital_elements(d)

        E0 = self.M + self.e * math.sin(self.M) * (1 + self.e * math.cos(self.M))  
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
        r = math.sqrt(xeclip**2 + yeclip**2) 

        self.start_angle = degrees(self.N + self.w)
        self.orbit_changed = True
        self.polar_coords = (r, longt)

    def truncate_trajectory(self, t):
        pass

    def clear_trajectory(self):
        pass
