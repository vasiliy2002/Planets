import configs.config as config
import utils
import datetime as dt
import math

class Sun():
    def __init__(self, sun_color, sun_graphic, line_graphic, label, name='Солнце'):
        self.sun_graphic = sun_graphic
        self.name = name
        self.origin = None
        self.label = label
        self.line_graphic = line_graphic
        self.line = list()
        self.sun_color = sun_color
        self.visible = True
        self.label_visible = True
        self.time_limit = dt.timedelta(days=365)
        self.last_t = None

    def set_label_visible(self, vis):
        self.label_visible = vis
        self.label.opacity = int(vis and self.visible)

    def set_visible(self, vis):
        self.visible = vis
        self.sun_color.a = int(vis)
        self.label.opacity = int(vis and self.label_visible)

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
        self.sun_graphic.pos = (widget_coords[0] - config.PLANET_SIZE, widget_coords[1] - config.PLANET_SIZE)
        self.label.pos = (self.sun_graphic.pos[0] - self.label.size[0] // 2 + config.PLANET_SIZE, self.sun_graphic.pos[1] + config.PLANET_SIZE*2)

        if self.origin and self.visible:
            self.update_trajectory(widget_coords)
        else:
            self.line = list()
            self.line_graphic.points = list()

    def update_size(self, cx, cy, w, h, scale):
        if not self.origin:
            return

        x, y = self.get_origin_coords()
        widget_coords = utils.coords2window(x, y, cx, cy, w, h, scale)
        self.sun_graphic.pos = (widget_coords[0] - config.MASS_CENTER_SIZE/2, widget_coords[1] - config.MASS_CENTER_SIZE/2)
        
        size = min(w, h)
        for i in range(len(self.line_graphic.points)):
            if i % 2 == 0:
                self.line_graphic.points[i] = utils.coord2window(self.line[i//2][0], cx, size, scale)
            else:
                self.line_graphic.points[i] = utils.coord2window(self.line[i//2][1], cy, size, scale)

    def get_xy(self):
        return 0, 0

    def update_pos(self, time):
        self.last_t = time

