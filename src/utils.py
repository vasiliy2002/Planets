from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.label import Label
import configs.config as config
import math
from kivy.uix.dropdown import DropDown
from styles import styles_dict
from widgets import PlanetsPosesInfo


def get_centers_and_masses(planets):
    center_x, center_y = list(), list()
    mass = list()

    for planet in planets:
        center = planet.get_xy()
        center_x.append(center[0])
        center_y.append(center[1])
        mass.append(planet.mass)

    return center_x, center_y, mass

def coord2window(pos, c, size, scale):
    return c + pos * (size/2) * scale

def coords2window(pos_x, pos_y, cx, cy, w, h, scale):
    size = min(w, h)        
    return (int(cx + pos_x * (size/2) * scale), int(cy + pos_y * (size/2) * scale))


def build_canvas(mw):

    earthx, earthy = mw.planets[2].get_real_xy()
    planets_info = PlanetsPosesInfo(earthx, earthy, mw.planets, cols=3, col_default_width=150, row_default_height=30)

    mw.add_widget(planets_info)
    mw.planets_info = planets_info

    update_planets_info = lambda x: mw.update_planets_info()
    Clock.schedule_interval(update_planets_info, 1.0/2)

def build_control_panel(control_panel, mw, change_color):

    theme_layout = BoxLayout(spacing=10)
    theme_label = Label(text="Цветовая тема:")

    # Выбор цветовой темы
    dropdown = DropDown()
    dropdown_buttons = list()
    
    for key in styles_dict.keys():
        theme_btn = Button(text=key, size_hint_y=None)
        theme_btn.bind(on_release=lambda btn: (dropdown.select(btn.text), change_color(btn.text)))

        dropdown.add_widget(theme_btn)
        dropdown_buttons.append(theme_btn)
    
    dropdown_button = Button(text='Vintage NASA Blueprint')
    dropdown_buttons.append(dropdown_button)
    dropdown_button.bind(on_release=dropdown.open)

    dropdown.bind(on_select=lambda instance, x: setattr(dropdown_button, 'text', x))
    theme_layout.add_widget(theme_label)
    theme_layout.add_widget(dropdown_button)

    # Кнопка центра масс
    btn = Button(text="Центр масс", font_size=16)
    btn.bind(on_press=mw.draw_mass_center)

    # Измененние масштаба
    scale_layout = BoxLayout(spacing=10)
    
    scale_label = Label(text="Масштаб:")

    scale_plus_btn = Button(text="+", font_size=16)
    scale_plus_btn.bind(on_press=lambda instance: mw.rescale(instance, 1.5))

    scale_minus_btn = Button(text="-", font_size=16)
    scale_minus_btn.bind(on_press=lambda instance: mw.rescale(instance, 0.67))

    scale_layout.add_widget(scale_label)
    scale_layout.add_widget(scale_plus_btn)
    scale_layout.add_widget(scale_minus_btn)

    # Изменение скорости
    speed_layout = BoxLayout(spacing=10)
    speed_label = Label(text="Скорость:")

    speed_plus_btn = Button(text="+", font_size=16)
    speed_plus_btn.bind(on_press=lambda instance: mw.change_speed(instance, 1.5))

    speed_minus_btn = Button(text="-", font_size=16)
    speed_minus_btn.bind(on_press=lambda instance: mw.change_speed(instance, 0.67))

    speed_layout.add_widget(speed_label)
    speed_layout.add_widget(speed_plus_btn)
    speed_layout.add_widget(speed_minus_btn)

    # Пауза
    pause_btn = Button(text="Пауза", font_size=16)
    pause_btn.bind(on_press=mw.pause)
    mw.pause_btn = pause_btn

    # Метка с датой
    date_label = Label(font_size=30)

    control_panel.add_widget(theme_layout)
    control_panel.add_widget(btn)
    control_panel.add_widget(scale_layout)
    control_panel.add_widget(speed_layout)
    control_panel.add_widget(pause_btn)
    control_panel.add_widget(date_label)

    control_panel.buttons += dropdown_buttons
    control_panel.buttons += [btn, scale_plus_btn, scale_minus_btn, speed_plus_btn,
                                speed_minus_btn, pause_btn]
    control_panel.labels += [scale_label, speed_label, date_label, theme_label]

    Clock.schedule_interval(mw.update, 1.0/config.FPS)
    update_label_date = lambda x: mw.refresh_date(date_label)
    Clock.schedule_interval(update_label_date, 1.0/config.DATE_LABEL_REFRESH_RATE)

    Clock.schedule_once(lambda dt: change_color('Vintage NASA Blueprint'), 0.1)

def get_dist(firstx, firsty, secondx, secondy):
    return math.sqrt((firstx - secondx) ** 2 + (firsty - secondy) ** 2)


