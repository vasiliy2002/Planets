from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from styles import styles_dict
from kivy.uix.textinput import TextInput

import utils
import math

class AddTrack(BoxLayout):
    def __init__(self, scheme='sci-fi', **kwargs):
        super().__init__(**kwargs)
        
        self.name_layout = BoxLayout(spacing=10)
        self.object_name_label = Label(text="Название")
        self.text_input = TextInput()

        self.name_layout.add_widget(self.object_name_label)
        self.name_layout.add_widget(self.text_input)

        self.add_widget(self.name_layout)

        self.type_layout = BoxLayout(spacing=10)
        self.type_label = Label(text="Тип")
        


class PlanetsPosesInfo(GridLayout):
    def __init__(self, earthx, earthy, planets, **kwargs):
        super().__init__(**kwargs)    
        self.add_widget(Label(text='Объект'))
        self.add_widget(Label(text='Градус'))
        self.add_widget(Label(text='Расстояние от Земли (км)'))

        self.graduses, self.dists = list(), list()

        for planet in planets:
            self.add_widget(Label(text=planet.name))
            angle = (planet.polar_coords[1]/math.pi * 180 + planet.start_angle + 360) % 360
            angle = round(angle, 2)
            gradus = Label(text="-", halign='right')

            gradus.text_size[0] = gradus.size[0] - 53
            self.add_widget(gradus)
            self.graduses.append(gradus)

            planetx, planety = planet.get_xy()
            dist = utils.get_dist(earthx, earthy, planetx, planety)
            dist = int(dist)
            dist_label = Label(text="-", halign='right')
            dist_label.text_size[0] = dist_label.size[0] + 30

            self.add_widget(dist_label)
            self.dists.append(dist_label)


        self.add_widget(Label(text="Центр масс"))
        mx, my = self.get_mass_center_xy(planets)
        angle = self.xy2gradus(mx, my)
        angle = round(angle, 2)
        self.mc_angle = Label(text="-", halign='right')

        self.mc_angle.text_size[0] = self.mc_angle.size[0] - 53
        self.add_widget(self.mc_angle)

        dist = utils.get_dist(earthx, earthy, mx, my)
        dist = int(dist)
        self.mc_dist = Label(text="-", halign='right')
        self.mc_dist.text_size[0] = self.mc_dist.size[0] + 30
        self.add_widget(self.mc_dist)


    def get_mass_center_xy(self, planets):
        x, y = 0, 0
        sum_mass = 0
        for planet in planets:
            px, py = planet.get_xy()
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
            angle = (planet.polar_coords[1]/math.pi * 180 + planet.start_angle + 360) % 360
            angle = round(angle, 2)
            self.graduses[i].text = f"{angle:.2f}"

            planetx, planety = planet.get_xy()
            dist = utils.get_dist(earthx, earthy, planetx, planety)
            dist = int(dist)
            self.dists[i].text = f"{dist:_}".replace("_", " ")
        
        mx, my = self.get_mass_center_xy(planets)
        angle = self.xy2gradus(mx, my)
        angle = round(angle, 2)
        self.mc_angle.text = f"{angle:.2f}"

        dist = utils.get_dist(earthx, earthy, mx, my)
        dist = int(dist)
        self.mc_dist.text = f"{dist:_}".replace("_", " ")

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

        self.labels[-1].text_size = (self.width, None)

    def change_color(self, scheme='sci-fi'):
        theme = styles_dict[scheme]
        self.bg_color.rgba = theme['CONTROL_PANEL_COLOR']

        for label in self.labels:
            label.color = theme['TEXT_COLOR']

        for btn in self.buttons:
            btn.background_color = theme['BUTTONS_COLOR']
            btn.color = theme['TEXT_COLOR']


