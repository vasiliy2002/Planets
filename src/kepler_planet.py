import math
import configs.config as config
import utils


class KeplerPlanet:
    def __init__(self, name, mass, period, start_angle, perihelion_time, eccentricity, a, orbit_graphic, planet_graphic, rotation_graphic, orbit_data=None):
        self.name = name
        self.mass = mass

        self.period = period
        self.start_angle = start_angle
        self.perihelion_time = perihelion_time
        self.e = eccentricity
        self.a = a
        self.c = self.a * self.e
        self.b = self.a * math.sqrt(1 - self.e ** 2)

        # Графический объект орбиты и планеты
        self.orbit_graphic = orbit_graphic
        self.planet_graphic = planet_graphic
        self.rotation_graphic = rotation_graphic

        self.polar_coords = (1, 1)

        # Данные для уточнения орбиты
        self.orbit_data = orbit_data
        self.cur_year = 2000

        self.update_orbit = False

    def get_closest_orbit_data_year(self, year):
        min_year, max_year = min(self.orbit_data.keys()), max(self.orbit_data.keys())

        if year <= min_year:
            return min_year

        if year >= max_year:
            return max_year

        low = max([d for d in self.orbit_data if d <= year])
        high = min([d for d in self.orbit_data if d >= year])
        near_year = low if year - low <= high - year else high
        return near_year

    def update_orbit_params(self, year):
        year = 2000
        params = self.orbit_data[year]

        self.perihelion_time = params['perihelion']
        self.e = params['eccentricity']
        self.start_angle = params['angle']
        self.a = params['radius']
        self.period = params['period']

        self.c = self.a * self.e
        self.b = self.a * math.sqrt(1 - self.e ** 2)

        self.cur_year = year
        self.update_orbit = True


    def update_pos(self, t):
        period = self.period.total_seconds() / 86400
        time_since_perihelion = (t - self.perihelion_time) % period
        self.polar_coords = utils.get_pos(self.a, self.e, period, time_since_perihelion)
    
    def get_xy(self):
        r, phi = self.polar_coords
        x, y = math.cos(phi) * r, math.sin(phi) * r
        rx = x * math.cos(self.start_angle*math.pi/180) - y * math.sin(self.start_angle*math.pi/180)
        ry = x * math.sin(self.start_angle*math.pi/180) + y * math.cos(self.start_angle*math.pi/180)
        return rx, ry

    def get_planet_data(self):
        x, y = self.get_xy()
        r = math.sqrt(x ** 2 + y ** 2)
        phita = (math.degrees(math.atan2(y, x)) + 360) % 360

        return r, phita

    def update_graphic(self, cx, cy, w, h, scale):
        x, y = self.get_xy()
        widget_coords = utils.coords2window(x, y, cx, cy, w, h, scale)
        self.planet_graphic.pos = (widget_coords[0] - config.PLANET_SIZE/2, widget_coords[1] - config.PLANET_SIZE/2)       

    def update_size(self, cx, cy, w, h, scale):

        self.rotation_graphic.origin = (cx, cy)
        self.rotation_graphic.angle = self.start_angle
        self.orbit_graphic.ellipse = (w/2 - self.c*scale - self.a*scale, h/2 - self.b*scale, 2*self.a*scale, 2*self.b*scale)

        x, y = self.get_xy()
        widget_coords = utils.coords2window(x, y, cx, cy, w, h, scale)
        self.planet_graphic.pos = (widget_coords[0] - config.PLANET_SIZE/2, widget_coords[1] - config.PLANET_SIZE/2)


