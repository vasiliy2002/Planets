from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from styles import styles_dict

import utils
import math


class PlanetsPosesInfo(GridLayout):
    def __init__(self, earthx, earthy, planets, **kwargs):
        super().__init__(**kwargs)    
        self.add_widget(Label(text='Объект'))
        self.add_widget(Label(text='Градус'))
        self.add_widget(Label(text='Расстояние от Земли (а. е.)'))

        self.graduses, self.dists = list(), list()

        for planet in planets:
            self.add_widget(Label(text=planet.name))
            gradus = Label(text=str(round(planet.pos/math.pi * 180, 2)))
            self.add_widget(gradus)
            self.graduses.append(gradus)

            planetx, planety = planet.get_real_xy()
            dist = utils.get_dist(earthx, earthy, planetx, planety)
            dist_label = Label(text=str(round(dist, 2)))
            self.add_widget(dist_label)
            self.dists.append(dist_label)

        self.add_widget(Label(text="Центр масс"))
        mx, my = self.get_mass_center_xy(planets)
        angle = self.xy2gradus(mx, my)
        self.mc_angle = Label(text=str(round(angle, 2)))
        self.add_widget(self.mc_angle)

        dist = utils.get_dist(earthx, earthy, mx, my)
        self.mc_dist = Label(text=str(round(dist, 2)))
        self.add_widget(self.mc_dist)


    def get_mass_center_xy(self, planets):
        x, y = 0, 0
        sum_mass = 0
        for planet in planets:
            px, py = planet.get_real_xy()
            x += px * planet.mass
            y += py * planet.mass
            sum_mass += planet.mass
        x /= sum_mass
        y /= sum_mass
        return x, y

    def xy2gradus(self, x, y):
        r = math.sqrt(x**2 + y**2)
        x, y = x / r, y / r
        angle = math.acos(x)
        if y < 0:
            angle *= -1
        angle = (angle + 2 * math.pi) % (2 * math.pi)
        angle = angle/math.pi*180
        return angle

    def update(self, earthx, earthy, planets):
        for i, planet in enumerate(planets):
            self.graduses[i].text = str(round(planet.pos/math.pi * 180, 2))

            planetx, planety = planet.get_real_xy()
            dist = utils.get_dist(earthx, earthy, planetx, planety)
            self.dists[i].text = str(round(dist, 2))
        
        mx, my = self.get_mass_center_xy(planets)
        angle = self.xy2gradus(mx, my)
        self.mc_angle.text = str(round(angle, 2))

        dist = utils.get_dist(earthx, earthy, mx, my)
        self.mc_dist.text = str(round(dist, 2))

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


