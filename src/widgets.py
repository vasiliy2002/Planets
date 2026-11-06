from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.graphics import Color, Rectangle
from styles import styles_dict
from kivy.uix.textinput import TextInput
from kivy.properties import NumericProperty
from functools import partial
from kivy.graphics import Line
import utils
import math
import datetime as dt
import configs.config as config
import numpy as np


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

class PlotImage(FloatLayout):
    time_span = NumericProperty(1)
    min_y = NumericProperty(1)
    max_y = NumericProperty(1E9)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self.bg_color = Color(*[0.08*2, 0.11*2, 0.11*2, 1.])
            self.background = Rectangle(pos=[self.pos[0] + self.width*0.15, self.pos[1] + self.height*0.1], size=(self.width*0.8, self.height*0.8))

            self.horizontal_lines = self.draw_hors()
            self.vert_lines = self.draw_verts()

        with self.canvas:
            self.planet_plots = list()
            for i in range(len(config.PLANET_COLORS)):
                Color(*config.PLANET_COLORS[i])
                self.planet_plots.append(Line(points=list(), width=2))

            Color(1.0, 0.85, 0.2, 1.0)
            self.sun_plot = Line(points=list(), width=2)

            Color(0.9, 0.9, 0.9, 0.9)
            self.mass_center_plot = Line(points=list(), width=2)

        self.xlabels = self.create_x_labels()
        self.ylabels = self.create_y_labels()
        self.rename_x_labels()
        self.rename_y_labels()

    def get_time_geometry(self, timestamp, cur_time):
        time_span_days = self.time_span * 365
        coord = (timestamp - cur_time) / time_span_days

        if coord < -1 or coord > 1:
            return -1

        center_coord = self.pos[0] + 0.55 * self.width
        return center_coord + coord * 0.4 * self.width

    def get_distance_geometry(self, distance):
        if distance < self.min_y or distance > self.max_y:
            return -1

        coord = (distance - self.min_y) / (self.max_y - self.min_y)
        return self.pos[1] + self.height * (0.1 + 0.8 * coord)

    def get_plot_geometry(self, plot_data, t):
        times = plot_data.get_times()
        time_span_days = self.time_span * 365
        coordx = (times - t) / time_span_days
        center_coord = self.pos[0] + 0.55 * self.width
        coordx = center_coord + coordx * 0.4 * self.width

        dists = plot_data.get_dists()
        coordy = (dists - self.min_y) / (self.max_y - self.min_y)
        coordy = self.pos[1] + self.height * (0.1 + 0.8 * coordy)

        coords = np.hstack([coordx[:, np.newaxis], coordy[:, np.newaxis]])

        coords = coords[(coords[:, 0] >= self.pos[0] + self.width * 0.15) & (coords[:, 0] <= self.pos[0] + self.width * 0.95)]
        coords = coords[(coords[:, 1] >= self.pos[1] + self.height * 0.1) & (coords[:, 1] <= self.pos[1] + self.height * 0.9)]

        return coords

    def draw_plot(self, plot, plot_data, t):
        xy = self.get_plot_geometry(plot_data, t)
        plot.points = xy.flatten().tolist()

    def draw_plots(self, dists_manager, t):
        for i in range(len(self.planet_plots)):
            if not dists_manager.planets[i].active:
                self.planet_plots[i].points = list()
                continue
            self.draw_plot(self.planet_plots[i], dists_manager.planets_dists[i], t)

        if dists_manager.sun.active:
            self.draw_plot(self.sun_plot, dists_manager.sun_dists, t)
        else:
            self.sun_plot.points = list()
        
        if dists_manager.mass_center.active:
            self.draw_plot(self.mass_center_plot, dists_manager.mass_center_dists, t)
        else:
            self.mass_center_plot.points = list()

    def draw_hors(self):
        # Сетка
        hor_lines = list()
        x1 = self.pos[0] + self.width * 0.15
        x2 = x1 + self.width * 0.8

        for i in range(5):
            with self.canvas.before:
                Color(1, 1, 1, 0.7)
                y1 = self.pos[1] + self.height * (0.1 + (0.95-0.15) * i / 4)
                y2 = y1
                hor_lines.append(Line(points=[x1, y1, x2, y2], width=1))
        return hor_lines

    def draw_verts(self):
        vert_lines = list()
        y1 = self.pos[1] + self.height * 0.1
        y2 = y1 + self.height * 0.8

        for i in range(7):
            with self.canvas.before:
                Color(1, 1, 1, 0.7)
                x1 = self.pos[0] + self.width * (0.15 + (0.9 - 0.1) * i / 6)
                x2 = x1
                vert_lines.append(Line(points=[x1, y1, x2, y2], width=1))
        return vert_lines

    def redraw_grid(self):
        x1 = self.pos[0] + self.width * 0.15
        x2 = x1 + self.width * 0.8

        for i in range(5):
            y1 = self.pos[1] + self.height * (0.1 + (0.95-0.15) * i / 4)
            y2 = y1
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

        y1 = self.pos[1] + self.height * 0.1
        y2 = y1 + self.height * 0.8

        for i in range(7):
            x1 = self.pos[0] + self.width * (0.15 + (0.9 - 0.1) * i / 6)
            x2 = x1
            self.vert_lines[i].points = [x1, y1, x2, y2]

    def rename_x_labels(self):
        half = len(self.xlabels) // 2
        self.xlabels[half].text = "сейчас"
        half_time = dt.timedelta(days=self.time_span*365)

        for i in range(1, half+1):
            cur_time = half_time / half * i
            string = "{} г. {} м.".format(cur_time.days // 365, (cur_time.days % 365) // 30)

            self.xlabels[half+i].text = "+" + string
            self.xlabels[half-i].text = "-" + string

    def on_time_span(self, instance, value):
        self.rename_x_labels()

    def on_min_y(self, instance, value):
        self.rename_y_labels()

    def on_max_y(self, instance, value):
        self.rename_y_labels()

    def rename_y_labels(self):
        value = int(self.min_y)
        self.ylabels[0].text = f"{value:_}".replace("_", " ")

        value = int(self.max_y)
        self.ylabels[-1].text = f"{value:_}".replace("_", " ")

        for i in range(1, len(self.ylabels)-1):
            value = int(self.min_y + i*(self.max_y - self.min_y) / (len(self.ylabels)-1))
            self.ylabels[i].text = f"{value:_}".replace("_", " ")

    def create_y_labels(self, num=5):
        labels = list()
        for i in range(num):
            label = Label(text=str(i), pos_hint={'right': 0.14, 'center_y': 0.1 + 0.8 / (num-1) * i}, size_hint=(None, 0.1))
            label.bind(texture_size=lambda instance, value: setattr(instance, 'width', value[0]))
            labels.append(label)
            self.add_widget(label)
        return labels

    def create_x_labels(self, num=7):
        labels = list()
        for i in range(num):
            label = Label(text=str(i)*7, pos_hint={'center_x': 0.15 + 0.8 / (num-1) * i, 'center_y': 0.03}, size_hint=(None, 0.1))
            label.bind(texture_size=lambda instance, value: setattr(instance, 'width', value[0]))
            labels.append(label)
            self.add_widget(label)
        return labels

    def on_size(self, instance, value):
        self.background.pos = [self.pos[0] + self.width*0.15, self.pos[1] + self.height*0.1]
        self.background.size = (self.width*0.8, self.height*0.8)
        self.redraw_grid()

    def on_pos(self, instance, value):
        self.background.pos = [self.pos[0] + self.width*0.15, self.pos[1] + self.height*0.1]
        self.background.size = (self.width*0.8, self.height*0.8)
        self.redraw_grid()

class PlotWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.handlers = [self.set_time_span, self.set_min_y, self.set_max_y]
        with self.canvas.before:
            self.bg_color = Color(*[0.08, 0.11, 0.11, 0.])
            self.background = Rectangle(pos=self.pos, size=(self.width, self.height))

    def set_time_span(self, instance):
        self.plot_image.time_span = instance.value

    def set_min_y(self, instance):
        if 1E5 ** instance.value >= self.plot_image.max_y - 1:
            instance.value = (math.log(self.plot_image.max_y, 1E5))
        self.plot_image.min_y = 1E5 ** instance.value

    def set_max_y(self, instance):
        if 1E5 ** instance.value <= self.plot_image.min_y + 1:
            instance.value = (math.log(self.plot_image.min_y, 1E5))
        self.plot_image.max_y = 1E5 ** instance.value

    def slider_touch(self, index, instance, value):
        self.handlers[index](instance)

    def create_plot(self):
        sliders_layout = BoxLayout(spacing=10, orientation='vertical', size_hint_x=0.35)
        slider_names = ['Диапозон времени:', 'Мин. y:', 'Макс. y:']
        sliders = list()
        for i, name in enumerate(slider_names):
            box_layout = BoxLayout(spacing=10)
            label = Label(text=name)

            max_val = 10 if i == 0 else 2
            val = 1 if i == 0 else i
            slider = Slider(min=1, max=max_val, value=val)

            slider.bind(value=partial(self.slider_touch, i))

            box_layout.add_widget(label)
            box_layout.add_widget(slider)
            sliders.append(slider)

            sliders_layout.add_widget(box_layout)

        self.add_widget(sliders_layout)

        plot_image = PlotImage()
        self.plot_image = plot_image
        self.plot_image.min_y = 1E5 ** sliders[1].value
        self.plot_image.max_y = 1E5 ** sliders[2].value
        self.add_widget(plot_image)
        self.bg_color.a = 1

    def on_size(self, instance, value):
        self.background.size = self.size

    def on_pos(self, instance, value):
        self.background.pos = self.pos       

    def set_visible(self, value):
        if value:
            self.create_plot()
        else:
            self.clear_widgets()
            self.bg_color.a = 0

class PlanetsPosesInfo(GridLayout):
    def __init__(self, earthx, earthy, planets, **kwargs):
        super().__init__(**kwargs)    
        self.add_widget(Label(text='Объект'))
        self.add_widget(Label(text='Градус'))
        self.add_widget(Label(text='Расстояние от Земли (км)'))

        self.graduses, self.dists = list(), list()

        for planet in planets:
            self.add_widget(Label(text=planet.name))
            angle = (planet.get_polar_coords()[1]/math.pi * 180 + planet.get_start_angle() + 360) % 360
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

    def change_opacity(self, opacity):
        for label in self.children:
            label.opacity = opacity

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
            angle = (planet.get_polar_coords()[1]/math.pi * 180 + planet.get_start_angle() + 360) % 360
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


