from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.core.window import Window
from planet import Planet
from mass_center import MassCenter
from consts import *
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty
from styles import styles_dict
from widgets import ControlPanel, PlotWidget
from moon import Moon
from dists_manager import DistsManager

import configs.config as config
import utils
import datetime as dt
from skyfield.api import load
from sun import Sun
from kepler_planet import KeplerBody
import math
from kivy.graphics import PushMatrix, PopMatrix, Rotate
from kivy.uix.label import Label
from graphic_manager import GraphicManager

ts = load.timescale()

# Задание размеров окна
Window.size = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)


class MainWidget(Widget):
    scale = NumericProperty(config.SCALE, min=0.01, max=300)


    def __init__(self, style='Vintage NASA Blueprint', **kwargs):
        super().__init__(**kwargs)

        theme = styles_dict[style]

        self.gm = GraphicManager()
        self.orbit_colors = list()
        self.planet_colors = list()
        self.mass_center = None
        self.time_speed = config.TIME_SEC
        self.fps = config.FPS
        self.root_time = config.ROOT_DATE
        self.time = config.START_DATE
        self.planets = list()
        self.moon = None
        self.mass_center_color = None
        self.red_dot_color = None
        self.mass_center_c = theme['MASS_CENTER']
        self.sun = None
        self.style = None
        self.trajectories_colors = list()
        max_radius = max(RADIUSES)

        cx, cy = self.center_x, self.center_y
        w, h = self.width, self.height

        self.gm.create_background(self.canvas.before, cx, cy, w, h, theme['SPACE_COLOR'])
        self.sun = utils.build_sun(self.gm, self.canvas, theme, self.add_widget)
        self.gm.create_body(self.canvas, 'Red dot', (1., 0., 0., 0.), 6)
        self.origin = self.sun

        for i in range(len(RADIUSES)):
            a = RADIUSES[i]
            e = ECCENTRICITIES[i]

            planet = utils.build_planet(self.gm, theme, config.PLANET_COLORS[i], self.add_widget, w, h, self.canvas,
                PLANET_NAMES[i], MASSES[i], PERIODS[i], ANGLES[i], PERIHELION[i], a, e, self.sun)
            self.planets.append(planet)

        self.moon = utils.build_moon(self.gm, self.canvas, "Луна", MOON_MASS, (0.85, 0.85, 0.85, 1.0), theme['ORBITS_COLOR'],
            self.add_widget, self.sun, self.planets[2], w, h)

        self.mass_center = utils.build_mass_center(self.gm, "Центр масс", self.canvas, theme['MASS_CENTER'], self.sun, self.add_widget)

        self.dists_manager = DistsManager(self.planets, self.sun, self.mass_center)

    def set_red_dot(self, checkbox, value):
        red_dot = self.gm.get_body_by_name("Red dot")
        red_dot.planet_graphic.color.a = int(value)

    def set_dists_table(self, checkbox, value):
        self.planets_info.change_opacity(int(value))

    def set_plot_visible(self, checkbox, value):
        self.plot_widget.set_visible(value)
        if not value:
            self.dists_manager.clear_dists()

    def set_labels(self, checkbox, value):
        self.sun.set_label_visible(value)
        self.moon.set_label_visible(value)
        self.mass_center.set_label_visible(value)

        for planet in self.planets:
            planet.set_label_visible(value)

    def set_visible(self, name, value):
        body = self.get_body_by_name(name)
        body.set_visible(value)

    def set_moon_orbit_scale(self, value):
        self.moon_orbit_label.text = str(round(value, 2)) + "x"
        self.moon.body_position.additional_scale = value

    def get_body_by_name(self, name):
        if name == 'Солнце':
            return self.sun
        elif name == 'Луна':
            return self.moon
        elif name == 'Центр масс':
            return self.mass_center
        else:
            for planet in self.planets:
                if planet.name == name:
                    return planet
        return None

    def change_origin(self, origin_name):
        body = self.get_body_by_name(origin_name)
        self.origin = body

        self.sun.change_origin(body)
        self.mass_center.change_origin(body)
        self.moon.change_origin(body)

        for planet in self.planets:
            planet.change_origin(body)

        self.dists_manager.clear_dists()

    def change_color(self, scheme):
        theme = styles_dict[scheme]
        self.style = theme

        self.gm.background.color.rgba = theme['SPACE_COLOR']

        for planet in self.planets:
            planet.change_orbit_color(theme['ORBITS_COLOR'])

        self.moon.change_orbit_color(theme['ORBITS_COLOR'])

    def draw_mass_center(self, instance):
        if instance.text == "Стереть":
            self.mass_center.set_visible(False)
            instance.text = "Центр масс"
        else:
            self.mass_center.set_visible(True)
            instance.text = "Стереть"

    def set_trajectory_length(self, instance):
        value, outer = instance.value, instance.outer
        value = math.exp(value)

        label, objects = list(), list()
        if outer:
            label = self.outer_trajectory_time_label
            objects = self.planets[4:] + [self.sun, self.mass_center]
        else:
            label = self.inner_trajectory_time_label
            objects = self.planets[:4]

        label.text = "years=" + str(round(value, 2))
        for obj in objects:
            obj.time_limit = dt.timedelta(value * 365)

    def on_size(self, instance, value):

        cx = self.center_x
        cy = self.center_y
        w = self.width 
        h = self.height
        
        self.gm.background.instruction.pos = self.pos
        self.gm.background.instruction.size = self.size

        self.planets_info.x = self.x
        self.planets_info.top = self.top

        self.plot_widget.size = (self.width, self.height // 3)
        self.plot_widget.pos = (self.x + w - self.width, 0)

        self.sun.update_size(cx, cy, w, h, self.scale)
        red_dot = self.gm.get_body_by_name("Red dot")
        red_dot.planet_graphic.instruction.pos = (w//2 - 3, h//2 - 3)

        for planet in self.planets:
            planet.update_size(cx, cy, w, h, self.scale)

        self.mass_center.update_size(cx, cy, w, h, self.scale)
    
    def update_planets_info(self):
        earthx, earthy = self.planets[2].get_xy()
        self.planets_info.update(earthx, earthy, self.planets)

    def update_poses(self):
        self.time += self.time_speed / self.fps

        self.sun.update_pos(self.time)

        for planet in self.planets:
            planet.update_pos(self.time)

        self.moon.update_pos(self.time)

        center_x, center_y, masses = utils.get_centers_and_masses(self.planets)
        self.mass_center.update_pos(self.time, centers_x=center_x, centers_y=center_y, masses=masses)

        if self.plot_widget.bg_color.a != 0:
            self.dists_manager.log_dists(self.time)

    def draw_plots(self, delta_t):
        if self.plot_widget.bg_color.a != 0:
            self.plot_widget.plot_image.draw_plots(self.dists_manager, self.time)

    def append_trajectories(self):
        self.sun.append_trajectory(self.time)

        for planet in self.planets:
            planet.append_trajectory(self.time)

        self.mass_center.append_trajectory(self.time)

    def update_graphic(self, cx, cy, w, h):
        for planet in self.planets:
            planet.update_graphic(cx, cy, w, h, self.scale)

        self.moon.update_graphic(cx, cy, w, h, self.scale)
        self.sun.update_graphic(cx, cy, w, h, self.scale)
        self.mass_center.update_graphic(cx, cy, w, h, self.scale)

    def update(self, delta_t):
        self.update_poses()
        self.append_trajectories()

        cx = self.center_x
        cy = self.center_y
        w = self.width 
        h = self.height

        self.update_graphic(cx, cy, w, h)

    def mul_scale(self, mul):
        value = self.scale * mul
        self.scale = max(config.MIN_SCALE, min(value, config.MAX_SCALE))
        self.change_scale(None, None)

    def rescale(self, instance, k):
        self.mul_scale(k)

    def on_touch_down(self, touch):
        if touch.button == 'scrollup':
            self.mul_scale(1 / config.SCROLL_SCALE_VALUE)
        elif touch.button == 'scrolldown':
            self.mul_scale(config.SCROLL_SCALE_VALUE)
        else:
            return super().on_touch_down(touch)

        return True

    def change_scale(self, instance, value):
        self.on_size(None, None)

    def refresh_date(self, label):
        label.text = self.time.utc_jpl()[:-12] 

    def change_speed(self, instance, k):
        if self.time_speed == dt.timedelta(0):
            self.time_speed = dt.timedelta(hours=12) if k > 1 else dt.timedelta(hours=-12)
            self.pause_btn.text = "Пауза"
            self.pause_btn.disabled = False
            return

        if self.time_speed < dt.timedelta(0):
            k = 1 / k

        self.time_speed *= k
        if abs(self.time_speed) < dt.timedelta(hours=12):
            self.time_speed = -dt.timedelta(hours=12) if self.time_speed > dt.timedelta(0) else dt.timedelta(hours=12) 

    def pause(self, instance):
        self.time_speed = dt.timedelta(0)
        instance.text = "Движение планет прекращено"
        instance.disabled = True

    def set_date(self, date_input, pause_btn, date_dropdown_btn):
        date = date_input.text
        date = date_dropdown_btn.text + " " + date
        
        if not utils.verify_date(date):
            date_input.text = "Неверный формат даты"
            return

        year, month, day = utils.parse_date(date)
        self.time = ts.utc(year, month, day)

        self.sun.clear_trajectory()
        self.mass_center.clear_trajectory()

        for planet in self.planets:
            planet.clear_trajectory()

        self.pause(pause_btn)


class PlanetsApp(App):
    def change_color_scheme(self, scheme):
        self.mw.change_color(scheme)
        self.control_panel.change_color(scheme)

    def build(self):
        layout = BoxLayout()
        self.mw = MainWidget()
        self.control_panel = ControlPanel(spacing=10, orientation='horizontal', size_hint_x=0.4)

        layout.add_widget(self.mw)
        layout.add_widget(self.control_panel)

        utils.build_canvas(self.mw)
        utils.build_control_panel(self.control_panel, self.mw, self.change_color_scheme)
        self.change_color_scheme('Vintage NASA Blueprint')

        return layout

if __name__ == "__main__":
    PlanetsApp().run()





