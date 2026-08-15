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

import configs.config as config
import utils
import datetime as dt

# Задание размеров окна
Window.size = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)


class MainWidget(Widget):
    scale = NumericProperty(config.SCALE, min=0.01, max=300)


    def __init__(self, style='sci-fi', **kwargs):
        super().__init__(**kwargs)

        theme = styles_dict[style]

        self.orbit_colors = list()
        self.planet_colors = list()
        self.mass_center = None
        self.time_speed = config.TIME_SEC
        self.fps = config.FPS
        self.time = config.START_DATE
        self.planets = list()
        self.mass_center_color = None
        self.mass_center_c = theme['MASS_CENTER']
        max_radius = max(RADIUSES)

        with self.canvas.before:
            self.bg_color = Color(*theme['SPACE_COLOR'])
            self.backgournd = Rectangle(pos=(self.center_x, self.center_y), size=(self.width, self.height))
        
        for i in range(len(RADIUSES)):

            with self.canvas:
                self.orbit_colors.append(Color(*theme['ORBITS_COLOR']))
                orbit_graphic = Line(circle=(self.width/2, self.height/2, 1), width=config.ORBIT_LINEWIDTH)

                self.planet_colors.append(Color(*theme['PLANETS_COLOR']))
                planet_graphic = Ellipse(size=(config.PLANET_SIZE, config.PLANET_SIZE))
        
            planet = Planet(self.time, MASSES[i], RADIUSES[i], PERIODS[i], (RADIUSES[i] / max_radius),
                                orbit_graphic, planet_graphic, config.START_POS[i])
            self.planets.append(planet)

    def change_color(self, scheme):
        theme = styles_dict[scheme]
        self.bg_color.rgba = theme['SPACE_COLOR']

        for c in self.orbit_colors:
            c.rgba = theme['ORBITS_COLOR']

        for c in self.planet_colors:
            c.rgba = theme['PLANETS_COLOR']

        self.mass_center_c = theme['MASS_CENTER']

        if self.mass_center_color:
            self.mass_center_color.rgba = self.mass_center_c

    def draw_mass_center(self, instance):
        if self.mass_center:
            self.canvas.remove(self.mass_center.mass_center_graphic)
            self.canvas.remove(self.mass_center.line_graphic)
            self.mass_center = None
            self.mass_center_color = None
            instance.text = "Центр масс"
        else:
            with self.canvas:
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

        for planet in self.planets:
            planet.update_size(cx, cy, w, h, self.scale)

        if self.mass_center:
            center_x, center_y, masses = utils.get_centers_and_masses(self.planets)
            self.mass_center.update_size(cx, cy, w, h, self.scale)
    
    def update_poses(self):
        self.time += self.time_speed / self.fps

        for planet in self.planets:
            planet.update_pos(self.time)

        if self.mass_center:
            center_x, center_y, masses = utils.get_centers_and_masses(self.planets)
            self.mass_center.update_pos(center_x, center_y, masses)

    def update_graphic(self, cx, cy, w, h):
        for planet in self.planets:
            planet.update_graphic(cx, cy, w, h, self.scale)

        if self.mass_center:
            self.mass_center.update_graphic(cx, cy, w, h, self.scale)

    def update(self, dt):
        self.update_poses()

        cx = self.center_x
        cy = self.center_y
        w = self.width 
        h = self.height

        self.update_graphic(cx, cy, w, h)

    def mul_scale(self, mul):
        value = round(self.scale * mul, 2)
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
            self.time_speed = dt.timedelta(hours=2) if k > 1 else dt.timedelta(hours=-2)
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

class ControlPanel(BoxLayout):
    def __init__(self, scheme='sci-fi', **kwargs):
        super().__init__(**kwargs)
        self.buttons = list()
        self.labels = list()

        theme = styles_dict[scheme]

        with self.canvas.before:
            self.bg_color = Color(*theme['CONTROL_PANEL_COLOR'])
            self.backgournd = Rectangle(pos=(self.center_x, self.center_y), size=(self.width, self.height))

    def on_size(self, instance, value):
        self.backgournd.pos = self.pos
        self.backgournd.size = self.size

    def change_color(self, scheme='sci-fi'):
        theme = styles_dict[scheme]
        self.bg_color.rgba = theme['CONTROL_PANEL_COLOR']

        for label in self.labels:
            label.color = theme['TEXT_COLOR']

        for btn in self.buttons:
            btn.background_color = theme['BUTTONS_COLOR']
            btn.color = theme['TEXT_COLOR']

class PlanetsApp(App):
    def change_color_scheme(self, scheme):
        self.mw.change_color(scheme)
        self.control_panel.change_color(scheme)

    def build(self):
        layout = BoxLayout()
        self.mw = MainWidget()
        self.control_panel = ControlPanel(spacing=10, orientation='vertical', size_hint_x=0.25)

        layout.add_widget(self.mw)
        layout.add_widget(self.control_panel)

        utils.build_control_panel(self.control_panel, self.mw, self.change_color_scheme)
        self.change_color_scheme('sci-fi')

        return layout

if __name__ == "__main__":
    PlanetsApp().run()





