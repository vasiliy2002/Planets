from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, Line, SmoothLine
from kivy.core.window import Window
from planet import Planet
from mass_center import MassCenter
from kivy.clock import Clock
from consts import *
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView

import config
import utils

# TODO: разделить логику обновления позиций и отрисовки

# Задание размеров окна
Window.size = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)


class MainWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Масштаб
        self.scale = config.SCALE

        self.mass_center = None

        self.planets = list()
        max_radius = max(RADIUSES)

        for i in range(len(RADIUSES)):
            with self.canvas:
                Color(*config.ORBIT_COLOR)
                orbit_graphic = Line(circle=(self.width/2, self.height/2, 1), width=config.ORBIT_LINEWIDTH)

                Color(*config.PLANET_COLOR)
                planet_graphic = Ellipse(size=(config.PLANET_SIZE, config.PLANET_SIZE))
        
            planet = Planet(MASSES[i], RADIUSES[i], PERIODS[i], (RADIUSES[i] / max_radius),
                                orbit_graphic, planet_graphic, config.START_POS[i])
            self.planets.append(planet)

    def draw_mass_center(self, instance):
        if self.mass_center:
            self.canvas.remove(self.mass_center.mass_center_graphic)
            self.canvas.remove(self.mass_center.line_graphic)
            self.mass_center = None
            instance.text = "Центр масс"
        else:
            with self.canvas:
                Color(*config.MASS_CENTER_COLOR)
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
        
        for planet in self.planets:
            planet.update_size(cx, cy, w, h, self.scale)

        if self.mass_center:
            center_x, center_y, masses = utils.get_centers_and_masses(self.planets)
            self.mass_center.update_size(cx, cy, w, h, self.scale)
    
    def update_poses(self):
        for planet in self.planets:
            planet.update_pos()

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

        
class PlanetsApp(App):
    def build(self):
        layout = BoxLayout(spacing=10)
        mw = MainWidget()
        btn = Button(text="Центр масс", size_hint=(0.3, 0.3), font_size=16)
        btn.bind(on_press=mw.draw_mass_center)

        layout.add_widget(mw)
        layout.add_widget(btn)

        Clock.schedule_interval(mw.update, 1.0/config.FPS)
        return layout

if __name__ == "__main__":
    PlanetsApp().run()








