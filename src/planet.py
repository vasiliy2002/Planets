import math
import configs.config as config
import utils


class Planet:
    def __init__(self, start_time, mass, radius, period, orbit_size, orbit_graphic, planet_graphic, pos):
        self.mass = mass

        self.start_time = start_time

        # Значения радиуса и периода из consts.py
        self.radius = radius
        self.period = period

        # Радиус орбиты (нормализован)
        self.orbit_size = orbit_size

        # Графический объект орбиты и планеты
        self.orbit_graphic = orbit_graphic
        self.planet_graphic = planet_graphic

        # Позиция из config.py
        self.pos = pos
        self.start_pos = pos


    def update_pos(self, t):
        period = self.period.total_seconds() / 86400
        self.pos = ( (t - self.start_time) % period ) / period * 2 * math.pi + self.start_pos
    
    def get_xy(self):
        return math.cos(self.pos) * self.orbit_size, math.sin(self.pos) * self.orbit_size 

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

