import utils
import math
import datetime as dt
from plot_data import PlotData


class DistsManager():
    def __init__(self, planets, sun, mass_center):
        self.planets = planets
        self.sun = sun
        self.mass_center = mass_center

        self.planets_dists = [PlotData() for i in range(len(self.planets))]
        self.sun_dists = PlotData()
        self.mass_center_dists = PlotData()

        self.min_t = None
        self.max_t = None

    def clear_dists(self):
        for pd in self.planets_dists:
            pd.clear()
        self.sun_dists.clear()
        self.mass_center_dists.clear()

    def update_poses(self, t):
        self.sun.update_pos(t)

        for planet in self.planets:
            planet.update_pos(t)

        center_x, center_y, masses = utils.get_centers_and_masses(self.planets)
        self.mass_center.update_pos(t, centers_x=center_x, centers_y=center_y, masses=masses)

    def log_dists(self, t):
        for i, planet in enumerate(self.planets):
            dx, dy = planet.body_position.get_origin_coords()
            self.planets_dists[i].add(t, math.sqrt(dx ** 2 + dy ** 2)) 

        dx, dy = self.sun.body_position.get_origin_coords()
        self.sun_dists.add(t, math.sqrt(dx ** 2 + dy ** 2))

        dx, dy = self.mass_center.body_position.get_origin_coords()
        self.mass_center_dists.add(t, math.sqrt(dx ** 2 + dy ** 2))

