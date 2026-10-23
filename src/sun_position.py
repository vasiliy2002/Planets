import math

class SunPosition():
    def __init__(self, origin=None):
        self.origin = origin
        self.line = list()
        self.orbit_changed = False

    def last_t(self):
        return self.line[-1][2]

    def get_xy(self):
        return 0, 0

    def get_polar_coords(self):
        pass

    def get_origin_coords(self):
        if not self.origin:
            return 0, 0
        else:
            x, y = self.get_xy()
            ox, oy = self.origin.get_xy()
            return x - ox, y - oy

    def update_pos(self, t, save_history=False):
        pass

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


