import math
import configs.config as config
import utils


class KeplerPlanet:
    def __init__(self, name, mass, period, start_angle, perihelion_time, eccentricity, a, orbit_graphic, planet_graphic):
        self.name = name
        self.mass = mass

        self.period = period
        self.start_angle = start_angle
        self.perihelion_time = perihelion_time
        self.eccentricity = eccentricity
        self.a = a

        # Графический объект орбиты и планеты
        self.orbit_graphic = orbit_graphic
        self.planet_graphic = planet_graphic

        self.polar_coords = (0, 0) 

    def update_pos(self, t):
        period = self.period.total_seconds() / 86400
        time_since_perihelion = (t - self.perihelion_time) % period
        self.polar_coords = utils.get_pos(self.a, self.eccentricity, period, time_since_perihelion)
    
    def get_xy(self):
        r, phi = self.polar_coords
        return math.cos(phi) * r, math.sin(phi) * r 

    def get_real_xy(self):
        r, phi = self.polar_coords
        return math.cos(phi) * r, math.sin(phi) * r 

    def update_graphic(self, cx, cy, w, h, scale):
        x, y = self.get_xy()
        widget_coords = utils.coords2window(x, y, cx, cy, w, h, scale)
        self.planet_graphic.pos = (widget_coords[0] - config.PLANET_SIZE/2, widget_coords[1] - config.PLANET_SIZE/2)        

    def update_size(self, cx, cy, w, h, scale):
        radius = min(w, h) * self.orbit_size * scale / 2
        self.orbit_graphic.circle = (cx, cy, radius)
        x, y = self.get_xy()
        widget_coords = utils.coords2window(x, y, cx, cy, w, h, scale)
        self.planet_graphic.pos = (widget_coords[0] - config.PLANET_SIZE/2, widget_coords[1] - config.PLANET_SIZE/2)


