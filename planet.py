import math
import config

class Planet:
    def __init__(self, radius, period, orbit_size, orbit_graphic, planet_graphic, pos):
        # Значения радиуса и периода из consts.py
        self.radius = radius
        self.period = period

        # Радиус орбиты по отношению к размеру окна
        self.orbit_size = orbit_size

        # Графический объект орбиты и планеты
        self.orbit_graphic = orbit_graphic
        self.planet_graphic = planet_graphic

        # Позиция из config.py
        self.pos = pos

    def update_pos(self):
        self.pos += math.pi * 2 / self.period
    
    def update_graphic(self, cx, cy, w, h, scale):
        radius = min(w, h) * self.orbit_size * scale
        self.orbit_graphic.circle = (cx, cy, radius)
        self.planet_graphic.pos = (int(cx + math.cos(self.pos) * radius - config.PLANET_SIZE/2), int(cy + math.sin(self.pos) * radius) - config.PLANET_SIZE/2)

    def update_planet(self, cx, cy, w, h, scale):
        self.update_pos()        
        radius = min(w, h) * self.orbit_size * scale
        self.planet_graphic.pos = (int(cx + math.cos(self.pos) * radius - config.PLANET_SIZE/2), int(cy + math.sin(self.pos) * radius) - config.PLANET_SIZE/2)        


