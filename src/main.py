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
from widgets import ControlPanel
from moon import Moon

import configs.config as config
import utils
import datetime as dt
from skyfield.api import load
from kepler_planet import KeplerPlanet
import math
from kivy.graphics import PushMatrix, PopMatrix, Rotate

ts = load.timescale()

# Задание размеров окна
Window.size = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)


class MainWidget(Widget):
    scale = NumericProperty(config.SCALE, min=0.01, max=300)


    def __init__(self, style='Vintage NASA Blueprint', **kwargs):
        super().__init__(**kwargs)

        theme = styles_dict[style]

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
        max_radius = max(RADIUSES)


        with self.canvas.before:
            self.bg_color = Color(*theme['SPACE_COLOR'])
            self.backgournd = Rectangle(pos=(self.center_x, self.center_y), size=(self.width, self.height))
        
        with self.canvas.before:
            self.sun_color = Color(*theme['SUN_COLOR'])
            self.sun_graphic = Ellipse(size=(config.PLANET_SIZE*2, config.PLANET_SIZE*2))

        with self.canvas:
            self.red_dot_color = Color(1.0, 0, 0, 0)
            self.dot = Ellipse(size=(6, 6))


        for i in range(len(RADIUSES)):
            with self.canvas.before:

                PushMatrix()
                start_angle = ANGLES[i]
                rotate_graphic = Rotate(angle=start_angle, axis=(0, 0, 1), origin=(self.width/2, self.height/2))
                self.orbit_colors.append(Color(*theme['ORBITS_COLOR']))
                
                a = RADIUSES[i]
                e = ECCENTRICITIES[i]
                c = a * e
                b = a * math.sqrt(1 - e ** 2)
                
                
                orbit_graphic = Line(ellipse=(self.width/2-c-a, self.height/2-b, 2*a, 2*b), width=1)
                PopMatrix()

                self.planet_colors.append(Color(*theme['PLANETS_COLOR']))
                planet_graphic = Ellipse(size=(config.PLANET_SIZE, config.PLANET_SIZE))

            kepler_planet = KeplerPlanet(PLANET_NAMES[i], MASSES[i], PERIODS[i], 
                start_angle, PERIHELION[i], e, a, orbit_graphic, planet_graphic, rotate_graphic)
            self.planets.append(kepler_planet)
        
        with self.canvas.before:
            PushMatrix()
            start_angle = 0
            rotate_graphic = Rotate(angle=start_angle, axis=(0, 0, 1), origin=(self.width/2, self.height/2))
            self.orbit_colors.append(Color(0., 1., 0, 1))

            orbit_graphic = Line(ellipse=(self.width/2, self.height/2, 200, 200), width=1)
            PopMatrix()

            self.planet_colors.append(Color(*theme['PLANETS_COLOR']))
            planet_graphic = Ellipse(size=(config.PLANET_SIZE, config.PLANET_SIZE))

        self.moon = Moon(orbit_graphic, planet_graphic, rotate_graphic)

        self.update_poses()

    def set_red_dot(self, checkbox, value):
        self.red_dot_color.a = int(value)

    def set_moon_orbit_scale(self, value):
        self.moon_orbit_label.text = str(round(value, 2)) + "x"
        self.moon.additional_scale = value

    def change_color(self, scheme):
        theme = styles_dict[scheme]

        self.sun_color.rgba = theme['PLANETS_COLOR'] #[min(1, 1.1 * x) for x in theme['PLANETS_COLOR'][:3]] + [1.]
        self.bg_color.rgba = theme['SPACE_COLOR']

        self.mass_center_c = theme['MASS_CENTER']

        for c in self.planet_colors:
            c.rgba = theme['PLANETS_COLOR']

        for c in self.orbit_colors:
            c.rgba = theme['ORBITS_COLOR']

        if self.mass_center_color:
            self.mass_center_color.rgba = self.mass_center_c

    def draw_mass_center(self, instance):
        if self.mass_center:
            self.canvas.before.remove(self.mass_center.mass_center_graphic)
            self.canvas.before.remove(self.mass_center.line_graphic)
            self.mass_center = None
            self.mass_center_color = None
            instance.text = "Центр масс"
        else:
            with self.canvas.before:
                self.mass_center_color = Color(*self.mass_center_c)
                mass_center_graphic = Ellipse(size=(config.PLANET_SIZE, config.PLANET_SIZE))
                line_graphic = Line(width=config.MASS_CENTER_LINEWIDTH)
            center_x, center_y, masses = utils.get_centers_and_masses(self.planets)
            self.mass_center = MassCenter(mass_center_graphic, line_graphic, center_x, center_y, masses)
            instance.text = "Стереть"

    def on_size(self, instance, value):


        cx = self.center_x
        cy = self.center_y
        w = self.width 
        h = self.height
        
        self.backgournd.pos = self.pos
        self.backgournd.size = self.size

        self.planets_info.x = self.x
        self.planets_info.top = self.top

        self.sun_graphic.pos = (w // 2 - config.PLANET_SIZE, h // 2 - config.PLANET_SIZE)
        self.dot.pos = (w//2 - 3, h//2 - 3)

        for planet in self.planets:
            planet.update_size(cx, cy, w, h, self.scale)

        self.moon.origin = self.planets[2].get_xy()
        self.moon.update_graphic(cx, cy, w, h, self.scale)

        if self.mass_center:
            center_x, center_y, masses = utils.get_centers_and_masses(self.planets)
            self.mass_center.update_size(cx, cy, w, h, self.scale)
    
    def update_planets_info(self):
        earthx, earthy = self.planets[2].get_xy()
        self.planets_info.update(earthx, earthy, self.planets)

    def update_poses(self):
        self.time += self.time_speed / self.fps

        for planet in self.planets:
            planet.update_pos(self.time)

        self.moon.update_pos(self.time)

        if self.mass_center:
            center_x, center_y, masses = utils.get_centers_and_masses(self.planets)
            self.mass_center.update_pos(center_x, center_y, masses)

    def update_graphic(self, cx, cy, w, h):
        for planet in self.planets:
            planet.update_graphic(cx, cy, w, h, self.scale)

        self.moon.origin = self.planets[2].get_xy()
        self.moon.update_graphic(cx, cy, w, h, self.scale)

        if self.mass_center:
            self.mass_center.update_graphic(cx, cy, w, h, self.scale)

    def update(self, dt):
        self.update_poses()

        cx = self.center_x
        cy = self.center_y
        w = self.width 
        h = self.height

        if self.planets[-3].update_orbit:
            self.planets[-3].update_size(cx, cy, w, h, self.scale)
            self.planets[-3].update_orbit = False

        self.update_graphic(cx, cy, w, h)

    def mul_scale(self, mul):
        value = self.scale * mul
        self.scale = max(config.MIN_SCALE, min(value, config.MAX_SCALE))

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

    def on_scale(self, instance, value):
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
        self.pause(pause_btn)


class PlanetsApp(App):
    def change_color_scheme(self, scheme):
        self.mw.change_color(scheme)
        self.control_panel.change_color(scheme)

    def build(self):
        layout = BoxLayout()
        self.mw = MainWidget()
        self.control_panel = ControlPanel(spacing=10, orientation='horizontal', size_hint_x=0.35)

        layout.add_widget(self.mw)
        layout.add_widget(self.control_panel)

        utils.build_canvas(self.mw)
        utils.build_control_panel(self.control_panel, self.mw, self.change_color_scheme)
        self.change_color_scheme('Vintage NASA Blueprint')

        return layout

if __name__ == "__main__":
    PlanetsApp().run()





