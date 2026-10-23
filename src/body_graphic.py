import utils

class BodyGraphic():
    def __init__(self, name, planet_graphic, orbit_graphic=None, line_graphic=None):
        self.name = name
        self.planet_graphic = planet_graphic
        self.orbit_graphic = orbit_graphic
        self.line_graphic = line_graphic
        self.t = list()

    def truncate_trajectory(self, trace_limit):
        if len(self.t) < 2:
            return

        time_limit = trace_limit.total_seconds() / 86400
        left_t = self.t[0]
        right_t = self.t[-1]

        while len(self.t) >= 2 and abs(left_t - right_t) > time_limit:
            self.t.pop(0)
            self.line_graphic.instruction.points = self.line_graphic.instruction.points[2:]
            left_t = self.t[0]

    def update_body_graphic(self, x, y, cg, t=None, trace=False):
        widget_coords = utils.coords2window(x, y, cg.cx, cg.cy, cg.w, cg.h, cg.scale)
        body_size = self.planet_graphic.instruction.size
        self.planet_graphic.instruction.pos = (widget_coords[0] - body_size[0]/2, widget_coords[1] - body_size[1]/2)

        if trace and t is not None:
            self.line_graphic.instruction.points += widget_coords
            self.t.append(t)

    def update_orbit(self, cg, start_angle, a, b, c, rot_x=None, rot_y=None, additional_scale=1):
        cx, cy = cg.cx, cg.cy
        if rot_x != None and rot_y != None:
            cx, cy = rot_x, rot_y

        self.orbit_graphic.rotation.origin = (cx, cy)
        self.orbit_graphic.rotation.angle = start_angle
        self.orbit_graphic.instruction.ellipse = (cx - c*cg.scale*additional_scale - a*cg.scale*additional_scale, cy - b*cg.scale*additional_scale, 2*a*cg.scale*additional_scale, 2*b*cg.scale*additional_scale)

    def update_trace_size(self, line, cg):
        new_points = list()
        for i in range(len(self.line_graphic.instruction.points)):
            j = i % 2
            new_points.append(utils.coord2window(line[i//2][j], [cg.cx, cg.cy][j], cg.scale))

        self.line_graphic.instruction.points = new_points


    def update_size(self, x, y, cg, trace_line=None, a=None, b=None, c=None, start_angle=None, rot_x=None, rot_y=None, additional_scale=1):
        self.update_body_graphic(x, y, cg)

        if self.orbit_graphic:
            cx, cy = cg.cx, cg.cy
            if self.name == 'Луна':
                cx, cy = self.earth_pos.get_xy()
                cx, cy = utils.coords2window(x, y, cg.cx, cg.cy, cg.w, cg.h, cg.scale)
            self.update_orbit(cg, start_angle, a, b, c, rot_x, rot_y, additional_scale)

        if self.line_graphic:
            self.update_trace_size(trace_line, cg)

    def clear_trajectory(self):
        self.t = list()
        if self.line_graphic:
            self.line_graphic.instruction.points = list()

    def set_body_visible(self, visible):
        self.planet_graphic.color.a = int(visible)
        if self.line_graphic:
            self.line_graphic.color.a = int(visible)

    def set_orbit_visible(self, visible):
        if self.orbit_graphic:
            self.orbit_graphic.color.a = int(visible) * self.orbit_graphic.alpha_channel


