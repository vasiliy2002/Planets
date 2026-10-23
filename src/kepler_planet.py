import math
import configs.config as config
import utils
import datetime as dt
from canvas_geometry import CanvasGeometry


class KeplerBody:
    def __init__(self, name, mass, label, body_position, body_graphics, origin, show_trace, active, show_label=True):
        self.name = name
        self.mass = mass
        self.label = label
        self.body_position = body_position
        self.body_graphics = body_graphics
        self.origin = origin
        self.time_limit = dt.timedelta(days=365)
        self.show_trace = show_trace
        self.show_label = show_label
        self.active = active

    def change_origin(self, origin):
        if origin.name == self.name:
            origin = None

        self.origin = origin
        self.body_position.origin = None if not origin else origin.body_position
        self.clear_trajectory()

        self.body_graphics.set_orbit_visible(self.active and (origin is not None) and (origin.name == "Солнце"))

    def clear_trajectory(self):
        self.body_position.clear_trajectory()
        self.body_graphics.clear_trajectory()

    def set_label_visible(self, visible):
        self.show_label = visible
        self.label.opacity = int((self.show_label) and (self.active))

    def set_visible(self, visible):
        self.active = visible
        self.set_label_visible(self.show_label)
        self.body_graphics.set_body_visible(visible)
        if self.origin and self.origin.name == 'Солнце':
            self.body_graphics.set_orbit_visible(visible)

    def trace_status(self):
        return (self.origin != None) and ((self.origin.name != "Солнце") or (self.name == "Центр масс")) and self.active and self.show_trace

    def update_pos(self, t, **kwargs):
        self.body_position.update_pos(t, **kwargs)

    def append_trajectory(self, t):
        if self.trace_status():
            self.body_position.append_trajectory(t)

    def update_graphic(self, cx, cy, w, h, scale):
        x, y = self.body_position.get_origin_coords()
        cg = CanvasGeometry(cx, cy, w, h, scale)
        trace = self.trace_status()
        t = self.body_position.last_t() if (trace and 
            len(self.body_position.line) * 2 != len(self.body_graphics.line_graphic.instruction.points)) else None

        self.body_graphics.update_body_graphic(x, y, cg, t, trace)

        if self.body_position.orbit_changed:
            a, b, c = self.body_position.a, self.body_position.b, self.body_position.c
            start_angle = self.body_position.start_angle
            if self.name == "Луна":
                cx, cy = self.body_position.earth_pos.get_xy()
                cx, cy = utils.coords2window(cx, cy, cg.cx, cg.cy, cg.w, cg.h, cg.scale)
            self.body_graphics.update_orbit(cg, start_angle, a, b, c, cx, cy, self.body_position.additional_scale)
            self.body_position.orbit_changed = False

        self.body_position.truncate_trajectory(self.time_limit)
        self.body_graphics.truncate_trajectory(self.time_limit)
        self.update_label()

        if not trace:
            self.body_position.clear_trajectory()
            self.body_graphics.clear_trajectory()

    def update_size(self, cx, cy, w, h, scale):
        x, y = self.body_position.get_origin_coords()
        cg = CanvasGeometry(cx, cy, w, h, scale)
        trace_line = self.body_position.line
        
        a, b, c, start_angle = None, None, None, None
        if self.body_graphics.orbit_graphic:
            a, b, c = self.body_position.a, self.body_position.b, self.body_position.c
            start_angle = self.body_position.start_angle

        self.body_graphics.update_size(x, y, cg, trace_line, a, b, c, start_angle)

        self.update_label()

    def update_label(self):
        ellipse = self.body_graphics.planet_graphic.instruction
        self.label.pos = (ellipse.pos[0] - self.label.size[0] // 2 + ellipse.size[0] // 2, ellipse.pos[1] + ellipse.size[0])

    def change_orbit_color(self, color):
        if self.body_graphics.orbit_graphic.color.a > 0:
            self.body_graphics.orbit_graphic.color.a = color[-1]
        self.body_graphics.orbit_graphic.alpha_channel = color[-1]
        self.body_graphics.orbit_graphic.color.rgb = color[:-1]

    def get_xy(self):
        return self.body_position.get_xy()

    def get_polar_coords(self):
        return self.body_position.get_polar_coords()

    def get_start_angle(self):
        return self.body_position.start_angle
