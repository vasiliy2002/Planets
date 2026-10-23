import utils
import math


class MassCenterPosition():
    def __init__(self, name, origin):
        self.name = name
        self.origin = origin
        self.pos = (1, 1)
        self.line = list()
        self.orbit_changed = False

    def last_t(self):
        return self.line[-1][2]

    def get_xy(self):
        return self.pos

    def get_polar_coords(self):
        return utils.xy2polar(*self.pos)

    def clear_trajectory(self):
        self.line = list()
        self.line_graphic.points = list()

    def get_origin_coords(self):
        if not self.origin:
            return 0, 0
        else:
            x, y = self.get_xy()
            ox, oy = self.origin.get_xy()
            return x - ox, y - oy

    def update_pos(self, t, **kwargs): #(self, centers_x, centers_y, masses, t, save_history=True):
        x, y = 0, 0

        centers_x = kwargs['centers_x']
        centers_y = kwargs['centers_y']
        masses = kwargs['masses']
        for i in range(len(centers_x)):
            x += masses[i] * centers_x[i]
            y += masses[i] * centers_y[i]
        x /= sum(masses)
        y /= sum(masses)

        self.pos = (x, y)

    def append_trajectory(self, t):
        x, y = self.get_origin_coords()
        
        if len(self.line) > 0:
            last_x, last_y = self.line[-1][0], self.line[-1][1]
            if math.sqrt((x - last_x) ** 2 + (y - last_y) ** 2) < 1e5:
                return
        
        self.line.append([x, y, t])


    def truncate_trajectory(self, time_limit):
        if len(self.line) < 2:
            return

        time_limit = time_limit.total_seconds() / 86400
        left_t = self.line[0][2]
        right_t = self.line[-1][2]

        while len(self.line) >= 2 and abs(left_t - right_t) > time_limit:
            self.line.pop(0)
            left_t = self.line[0][2]

    def clear_trajectory(self):
        self.line = list()

