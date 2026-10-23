import math
import utils


class KeplerPosition():
    def __init__(self, period, start_angle, perihelion_time, a, e, origin):
        self.period = period
        self.start_angle = start_angle
        self.perihelion_time = perihelion_time
        self.a = a
        self.e = e
        self.b = a * math.sqrt(1 - e ** 2)
        self.c = a * e
        self.polar_coords = (1, 1)
        self.origin = origin
        self.line = list()
        self.orbit_changed = False
        self.additional_scale = 1

    def last_t(self):
        if len(self.line) == 0:
            return None
        return self.line[-1][2]

    def get_xy(self):
        r, phi = self.polar_coords
        x, y = math.cos(phi) * r, math.sin(phi) * r
        rx = x * math.cos(self.start_angle*math.pi/180) - y * math.sin(self.start_angle*math.pi/180)
        ry = x * math.sin(self.start_angle*math.pi/180) + y * math.cos(self.start_angle*math.pi/180)
        return rx, ry

    def get_polar_coords(self):
        return self.polar_coords

    def get_origin_coords(self):
        if not self.origin:
            return 0, 0
        else:
            x, y = self.get_xy()
            ox, oy = self.origin.get_xy()
            return x - ox, y - oy

    def update_pos(self, t):
        period = self.period.total_seconds() / 86400
        time_since_perihelion = (t - self.perihelion_time) % period
        self.polar_coords = utils.get_pos(self.a, self.e, period, time_since_perihelion)

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

