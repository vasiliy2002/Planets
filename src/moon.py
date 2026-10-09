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

class Moon():
    def __init__(self, orbit_alpha, moon_color, orbit_color, orbit_graphic, planet_graphic, rotation_graphic, label, origin):
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

        self.earth_origin = (0, 0)
        self.polar_coords = (1, 1)
        self.additional_scale = 50

        self.label = label
        self.origin = origin

        self.moon_color = moon_color
        self.orbit_color = orbit_color

        self.orbit_alpha = orbit_alpha
        self.label_visible = True
        self.visible = True

    def set_label_visible(self, vis):
        self.label_visible = vis
        self.label.opacity = int(vis and self.visible)

    def set_orbit(self, vis):
        self.orbit_color.a = int(vis) * self.orbit_alpha

    def set_visible(self, vis):
        self.visible = vis

        orbit_vis = (self.origin != None) and (self.origin.name == "Солнце") and self.visible
        self.set_orbit(orbit_vis)

        self.moon_color.a = int(vis)
        self.label.opacity = int(vis and self.label_visible)

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

        E0 = self.M + self.e * math.sin(self.M) * (1 + self.e * math.cos(self.M)) #self.M if self.e <= 0.8 else math.pi
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

        self.polar_coords = (r, longt)

    def get_xy(self):
        r, phi = self.polar_coords
        x, y = r * math.cos(phi) * self.additional_scale, r * math.sin(phi) * self.additional_scale
        return self.earth_origin[0] + x, self.earth_origin[1] + y

    def get_origin_coords(self):
        if not self.origin:
            return 0, 0
        else:
            x, y = self.get_xy()
            ox, oy = self.origin.get_xy()
            return x - ox, y - oy

    def update_planet_graphic(self, cx, cy, w, h, scale):
        x, y = self.get_origin_coords()
        widget_coords = utils.coords2window(x, y, cx, cy, w, h, scale)
        self.planet_graphic.pos = (widget_coords[0] - config.PLANET_SIZE/2, widget_coords[1] - config.PLANET_SIZE/2)

    def update_orbit_graphic(self, cx, cy, w, h, scale):
        x, y = self.earth_origin
        origin_coords = utils.coords2window(x, y, cx, cy, w, h, scale)

        self.rotation_graphic.origin = origin_coords
        self.rotation_graphic.angle = degrees(self.N + self.w)
        self.orbit_graphic.ellipse = (origin_coords[0] - self.c*scale*self.additional_scale - self.a*scale*self.additional_scale, origin_coords[1] - self.b*scale*self.additional_scale, 2*self.a*scale*self.additional_scale, 2*self.b*scale*self.additional_scale)

    def update_graphic(self, cx, cy, w, h, scale):
        self.update_planet_graphic(cx, cy, w, h, scale)
        self.update_orbit_graphic(cx, cy, w, h, scale)
        self.label.pos = (self.planet_graphic.pos[0] - self.label.size[0] // 2 + config.PLANET_SIZE // 2, self.planet_graphic.pos[1] + config.PLANET_SIZE)


