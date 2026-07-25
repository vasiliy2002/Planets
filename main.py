from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
from kivy.core.window import Window
from planet import Planet
from kivy.clock import Clock
from consts import *
import config


# Задание размеров окна
Window.size = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)


class MainWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Масштаб
        self.scale = config.SCALE

        self.planets = list()
        max_radius = max(RADIUSES)

        for i in range(len(RADIUSES)):
            with self.canvas:
                Color(*config.ORBIT_COLOR)
                orbit_graphic = Line(circle=(self.width/2, self.height/2, 1), width=config.ORBIT_LINEWIDTH)

                Color(*config.PLANET_COLOR)
                planet_graphic = Ellipse(size=(config.PLANET_SIZE, config.PLANET_SIZE))
        
            planet = Planet(RADIUSES[i], PERIODS[i], (RADIUSES[i] / max_radius) / 2,
                                orbit_graphic, planet_graphic, config.START_POS[i])
            self.planets.append(planet)

    def on_size(self, instance, value):
        cx = self.center_x
        cy = self.center_y
        w = self.width 
        h = self.height
        
        for planet in self.planets:
            planet.update_graphic(cx, cy, w, h, self.scale)

    def run_planets(self, dt):
        cx = self.center_x
        cy = self.center_y
        w = self.width 
        h = self.height

        for planet in self.planets:
            planet.update_planet(cx, cy, w, h, self.scale)

class PlanetsApp(App):
    def build(self):
        mw = MainWidget()
        Clock.schedule_interval(mw.run_planets, 1.0/config.FPS)
        return mw

if __name__ == "__main__":
    PlanetsApp().run()








