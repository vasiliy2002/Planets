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
from sun import Sun
from kepler_planet import KeplerPlanet
import math
from kivy.graphics import PushMatrix, PopMatrix, Rotate
from kivy.uix.label import Label

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
        self.sun = None
        self.style = None
        self.trajectories_colors = list()
        max_radius = max(RADIUSES)


        with self.canvas.before:
            self.bg_color = Color(*theme['SPACE_COLOR'])
            self.backgournd = Rectangle(pos=(self.center_x, self.center_y), size=(self.width, self.height))
        
        with self.canvas:
            sun_color = Color(*theme['SUN_COLOR'])
            self.sun_color = sun_color
            sun_graphic = Ellipse(size=(config.PLANET_SIZE*2, config.PLANET_SIZE*2))
            line_graphic = Line(width=config.MASS_CENTER_LINEWIDTH)

        label = Label(text='Солнце', halign='center')
        label.text_size = label.size
        self.add_widget(label)

        self.sun = Sun(sun_color, sun_graphic, line_graphic, label)

        with self.canvas:
            self.red_dot_color = Color(1.0, 0, 0, 0)
            self.dot = Ellipse(size=(6, 6))


        for i in range(len(RADIUSES)):
            with self.canvas.before:

                PushMatrix()
                start_angle = ANGLES[i]
                rotate_graphic = Rotate(angle=start_angle, axis=(0, 0, 1), origin=(self.width/2, self.height/2))
                orbit_color = Color(*theme['ORBITS_COLOR'])
                orbit_alpha = orbit_color.a
                self.orbit_colors.append(orbit_color)
                
                a = RADIUSES[i]
                e = ECCENTRICITIES[i]
                c = a * e
                b = a * math.sqrt(1 - e ** 2)
                
                
                orbit_graphic = Line(ellipse=(self.width/2-c-a, self.height/2-b, 2*a, 2*b), width=1)
                PopMatrix()

                planet_color = Color(*config.PLANET_COLORS[i])
                self.planet_colors.append(planet_color)  #(Color(*theme['PLANETS_COLOR']))
                planet_graphic = Ellipse(size=(config.PLANET_SIZE, config.PLANET_SIZE))

                # line graphic
                tr_color = Color(*config.PLANET_COLORS[i]) #Color(*theme['PLANETS_COLOR'])
                self.trajectories_colors.append(tr_color)
                line_graphic = Line(width=config.MASS_CENTER_LINEWIDTH)

                label = Label(text=PLANET_NAMES[i], halign='center')
                label.text_size = label.size
                self.add_widget(label)

            kepler_planet = KeplerPlanet(PLANET_NAMES[i], MASSES[i], PERIODS[i], 
                start_angle, PERIHELION[i], e, a, orbit_alpha, orbit_color, planet_color, tr_color, orbit_graphic, planet_graphic, rotate_graphic, line_graphic, self.sun, label)
            self.planets.append(kepler_planet)
        
        with self.canvas.before:
            PushMatrix()
            start_angle = 0
            rotate_graphic = Rotate(angle=start_angle, axis=(0, 0, 1), origin=(self.width/2, self.height/2))

            orbit_color = Color(*theme['ORBITS_COLOR'])
            orbit_alpha = orbit_color.a
            self.orbit_colors.append(orbit_color)

            orbit_graphic = Line(ellipse=(self.width/2, self.height/2, 200, 200), width=1)
            PopMatrix()

            moon_color = Color(0.85, 0.85, 0.85, 1.0)
            self.planet_colors.append(moon_color)  #(Color(*theme['PLANETS_COLOR']))
            planet_graphic = Ellipse(size=(config.PLANET_SIZE, config.PLANET_SIZE))

        label = Label(text='Луна', halign='center')
        label.text_size = label.size
        self.add_widget(label)
        self.moon = Moon(orbit_alpha, moon_color, orbit_color, orbit_graphic, planet_graphic, rotate_graphic, label, self.sun)

        self.origin = self.sun

        with self.canvas.before:
            self.mass_center_color = Color(*self.mass_center_c)
            mass_center_graphic = Ellipse(size=(config.PLANET_SIZE, config.PLANET_SIZE))
            line_graphic = Line(width=config.MASS_CENTER_LINEWIDTH)

        label = Label(text='Центр масс', halign='center')
        label.text_size = label.size
        self.add_widget(label)

        center_x, center_y, masses = utils.get_centers_and_masses(self.planets)
        self.mass_center = MassCenter(self.mass_center_color, mass_center_graphic, line_graphic, center_x, center_y, masses, self.origin, "Центр масс", label, self.time)

        self.update_poses()

    def set_red_dot(self, checkbox, value):
        self.red_dot_color.a = int(value)

    def set_dists_table(self, checkbox, value):
        self.planets_info.change_opacity(int(value))

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
        self.moon.additional_scale = value

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
        print(origin_name)
        if not body:
            return

        self.origin = body
        self.mass_center.clear_trajectory()

        for planet in self.planets:
            planet.clear_trajectory()

        self.sun.clear_trajectory()

        self.sun.origin = body
        self.moon.origin = body
        self.mass_center.origin = body

        for planet in self.planets:
            planet.origin = body

        body.origin = None
        orbit_vis = origin_name == "Солнце"

        for planet in self.planets:
            if not planet.visible:
                continue
            planet.set_orbit(orbit_vis)
        
        if self.moon.visible:
            self.moon.set_orbit(orbit_vis)

    def change_color(self, scheme):
        theme = styles_dict[scheme]
        self.style = theme

        #self.sun_color.rgba = theme['PLANETS_COLOR']
        self.bg_color.rgba = theme['SPACE_COLOR']

        #self.mass_center_c = theme['MASS_CENTER'][:3] + [int(self.mass_center.visible)]
        """
        for c in self.planet_colors:
            c.rgba = theme['PLANETS_COLOR']
        """
        """
        for t in self.trajectories_colors:
            t.rgba = theme['PLANETS_COLOR']
        """
        for c in self.orbit_colors:
            c.rgb = theme['ORBITS_COLOR'][:-1]

        for planet in self.planets:
            planet.orbit_alpha = theme['ORBITS_COLOR'][-1]

        self.moon.orbit_alpha = theme['ORBITS_COLOR'][-1]
        #self.mass_center_color.rgba = self.mass_center_c

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
        
        self.backgournd.pos = self.pos
        self.backgournd.size = self.size

        self.planets_info.x = self.x
        self.planets_info.top = self.top

        self.sun.update_size(cx, cy, w, h, self.scale)
        self.dot.pos = (w//2 - 3, h//2 - 3)

        for planet in self.planets:
            planet.update_size(cx, cy, w, h, self.scale)

        self.moon.earth_origin = self.planets[2].get_xy()
        self.moon.update_graphic(cx, cy, w, h, self.scale)


        center_x, center_y, masses = utils.get_centers_and_masses(self.planets)
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
        self.mass_center.update_pos(center_x, center_y, masses, self.time)

    def update_graphic(self, cx, cy, w, h):
        for planet in self.planets:
            planet.update_graphic(cx, cy, w, h, self.scale)

        self.moon.earth_origin = self.planets[2].get_xy()
        self.moon.update_graphic(cx, cy, w, h, self.scale)

        self.sun.update_graphic(cx, cy, w, h, self.scale)

        self.mass_center.update_graphic(cx, cy, w, h, self.scale)

    def update(self, delta_t):
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





