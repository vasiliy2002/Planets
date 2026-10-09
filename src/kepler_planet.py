import math
import configs.config as config
import utils
import datetime as dt


class KeplerPlanet:
    def __init__(self, name, mass, period, start_angle, perihelion_time, eccentricity, a, orbit_alpha, orbit_color, planet_color, trajectory_color, orbit_graphic, planet_graphic, rotation_graphic, line_graphic, origin, label, orbit_data=None):
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
        self.line_graphic = line_graphic

        self.line = list()

        self.polar_coords = (1, 1)

        # Данные для уточнения орбиты
        self.orbit_data = orbit_data
        self.cur_year = 2000

        self.update_orbit = False
        self.origin = origin
        self.label = label

        self.orbit_alpha = orbit_alpha
        self.planet_color = planet_color
        self.orbit_color = orbit_color
        self.trajectory_color = trajectory_color
        self.visible = True

        self.label_visible = True
        self.time_limit = dt.timedelta(days=365)
        self.last_t = None

    def set_orbit(self, vis):
        self.orbit_color.a = int(vis) * self.orbit_alpha

    def set_visible(self, vis):
        self.visible = vis

        orbit_vis = (self.origin != None) and (self.origin.name == "Солнце") and self.visible
        self.set_orbit(orbit_vis)

        self.planet_color.a = int(vis)
        self.trajectory_color.a = int(vis)
        self.label.opacity = int(vis and self.label_visible)

    def set_label_visible(self, vis):
        self.label_visible = vis
        self.label.opacity = int(vis and self.visible)

    def clear_trajectory(self):
        self.line = list()
        self.line_graphic.points = list()

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


    def update_pos(self, t):
        period = self.period.total_seconds() / 86400
        time_since_perihelion = (t - self.perihelion_time) % period
        self.polar_coords = utils.get_pos(self.a, self.e, period, time_since_perihelion)
        self.last_t = t
    
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

    def get_origin_coords(self):
        if not self.origin:
            return 0, 0
        else:
            x, y = self.get_xy()
            ox, oy = self.origin.get_xy()
            return x - ox, y - oy

    def truncate_trajectory(self):
        if len(self.line) < 2:
            return

        time_limit = self.time_limit.total_seconds() / 86400
        left_t = self.line[0][2]
        right_t = self.line[-1][2]
        while len(self.line) >= 2 and abs(left_t - right_t) > time_limit:
            self.line.pop(0)
            self.line_graphic.points = self.line_graphic.points[2:]
            left_t = self.line[0][2]

    def update_trajectory(self, widget_coords):
        x, y = self.get_origin_coords()
        if len(self.line) > 1:
            last_x, last_y = self.line[-1][0], self.line[-1][1]
            if math.sqrt((x - last_x) ** 2 + (y - last_y) ** 2) < 0.1:
                return

        self.line.append([x, y, self.last_t])
        self.line_graphic.points += widget_coords
        self.truncate_trajectory()

    def update_graphic(self, cx, cy, w, h, scale):
        x, y = self.get_origin_coords()
        widget_coords = utils.coords2window(x, y, cx, cy, w, h, scale)
        self.planet_graphic.pos = (widget_coords[0] - config.PLANET_SIZE/2, widget_coords[1] - config.PLANET_SIZE/2)
        
        self.label.pos = (self.planet_graphic.pos[0] - self.label.size[0] // 2 + config.PLANET_SIZE // 2, self.planet_graphic.pos[1] + config.PLANET_SIZE)

        if not self.origin or self.origin.name == "Солнце" or not self.visible:
            self.line = list()
            self.line_graphic.points = list()
        else:
            self.update_trajectory(widget_coords)
            """
            x, y = self.get_origin_coords()
            self.line.append([x, y])
            self.line_graphic.points += widget_coords

            self.line_graphic.points = self.line_graphic.points[-1000:]
            self.line = self.line[-500:]
            """

    def __str__(self):
        return self.name

    def update_size(self, cx, cy, w, h, scale):
        self.rotation_graphic.origin = (cx, cy)
        self.rotation_graphic.angle = self.start_angle
        self.orbit_graphic.ellipse = (w/2 - self.c*scale - self.a*scale, h/2 - self.b*scale, 2*self.a*scale, 2*self.b*scale)

        x, y = self.get_origin_coords()

        widget_coords = utils.coords2window(x, y, cx, cy, w, h, scale)
        self.planet_graphic.pos = (widget_coords[0] - config.PLANET_SIZE/2, widget_coords[1] - config.PLANET_SIZE/2)

        self.label.pos = (self.planet_graphic.pos[0] - self.label.size[0] // 2 + config.PLANET_SIZE // 2, self.planet_graphic.pos[1] + config.PLANET_SIZE)

        size = min(w, h)
        for i in range(len(self.line_graphic.points)):
            if i % 2 == 0:
                self.line_graphic.points[i] = utils.coord2window(self.line[i//2][0], cx, size, scale)
            else:
                self.line_graphic.points[i] = utils.coord2window(self.line[i//2][1], cy, size, scale)
