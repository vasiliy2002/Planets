from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.label import Label
import configs.config as config
import math
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from styles import styles_dict
from widgets import PlanetsPosesInfo, AddTrack
from kivy.uix.popup import Popup
import re
from scipy import optimize
from kivy.uix.slider import Slider
from kivy.uix.checkbox import CheckBox
from consts import *

def radians(x):
    x = x % 360
    return (x * math.pi / 180)

def kepler_eq(E, M, e):
  return E - e * math.sin(E) - M

def get_phita(e, E):
  x = math.sqrt((1+e)/(1-e)) * math.tan(E/2)
  return 2 * math.atan2(x, 1)

def get_pos(a, e, P, t):
  n = 2 * math.pi / P
  M = n * t
  E0 = M if e <= 0.8 else math.pi
  E = optimize.newton(lambda x: kepler_eq(x, M, e), E0)

  phita = get_phita(e, E)
  r = a * (1 - e * math.cos(E))

  return r, phita

def verify_date(date_string):
    # 1. Check the general format using Regex
    # Matches 'A.D. ' or 'B.C. ' followed by 1-4 digit year, 1-2 digit month, and 1-2 digit day
    pattern = r"^(A\.D\.|B\.C\.) \d{1,6}-\d{1,2}-\d{1,2}$"
    
    if not re.match(pattern, date_string):
        return False
    return True

def parse_date(date_string):
    era = date_string[:4]
    era = 1 if era == "A.D." else -1
    year, month, day = [int(x) for x in date_string[5:].split("-")]
    if era < 0:
        year = -year + 1
    return year, month, day

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
    return c + pos * scale

def coords2window(pos_x, pos_y, cx, cy, w, h, scale):
    return (int(cx + pos_x*scale), int(cy + pos_y*scale))


def build_canvas(mw):

    earthx, earthy = mw.planets[2].get_xy()
    planets_info = PlanetsPosesInfo(earthx, earthy, mw.planets, cols=3, col_default_width=150, row_default_height=30)

    mw.add_widget(planets_info)
    mw.planets_info = planets_info

    update_planets_info = lambda x: mw.update_planets_info()
    Clock.schedule_interval(update_planets_info, 1.0/2)

def add_track(mw):
    popup = Popup(title='Новый объект', content=AddTrack(), size_hint=(0.3, 0.6))
    popup.open()

def build_control_panel(control_panel, mw, change_color):
    left_space, right_space = BoxLayout(spacing=10, orientation='vertical'), BoxLayout(spacing=10, orientation='vertical', size_hint_x=0.5)
    control_panel.add_widget(left_space)
    #control_panel.add_widget(right_space)

    # Построение правой стороны панели управления
    add_track_layout = BoxLayout(spacing=10)
    track_label = Label(text="Отслеживаемые объекты")
    add_track_button = Button(text="+", font_size=16, size_hint_x=0.3)
    add_track_button.bind(on_press=lambda instance: add_track(mw))

    add_track_layout.add_widget(track_label)
    add_track_layout.add_widget(add_track_button)

    right_space.add_widget(add_track_layout)
    #----------------------------------------------------

    # Построение левой стороны панели управления

    # Выбор цветовой темы
    theme_layout = BoxLayout(spacing=10)
    theme_label = Label(text="Цветовая тема:")
    
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

    # Выбор центра координат
    origin_layout = BoxLayout(spacing=10)
    origin_label = Label(text="Центр координат:")

    origin_dropdown = DropDown()
    origin_dropdown_buttons = list()

    for body in ['Центр масс', 'Солнце'] + PLANET_NAMES:
        origin_btn = Button(text=body, size_hint_y=None)
        origin_btn.bind(on_release=lambda btn: (origin_dropdown.select(btn.text), mw.change_origin(btn.text)))

        origin_dropdown.add_widget(origin_btn)
        origin_dropdown_buttons.append(origin_btn)

    origin_dropdown_button = Button(text='Солнце')
    origin_dropdown_buttons.append(origin_dropdown_button)
    origin_dropdown_button.bind(on_release=origin_dropdown.open)

    origin_dropdown.bind(on_select=lambda instance, x: setattr(origin_dropdown_button, 'text', x))
    origin_layout.add_widget(origin_label)
    origin_layout.add_widget(origin_dropdown_button)

    # Длина траектории
    trajectory_all_label = Label(text="Время учета позиций")

    trajectory_inner_layout, trajectory_outer_layout = BoxLayout(spacing=10), BoxLayout(spacing=10)
    static_labels = list()
    length_labels = list()

    for i, trajectory_layout in enumerate([trajectory_inner_layout, trajectory_outer_layout]):
        text = "Внешних планет:" if i else "Внутренних планет:"
        trajectory_length_label = Label(text=text, halign='center')
        trajectory_time_label = Label(text="years=1.0", halign='right', size_hint_x=0.3)
        
        static_labels.append(trajectory_length_label)
        length_labels.append(trajectory_time_label)
        
        trajectory_slider = Slider(min=-2, max=8, value=0)

        trajectory_slider.outer = i
        trajectory_slider.bind(on_touch_move=lambda instance, touch: mw.set_trajectory_length(instance))
        trajectory_slider.bind(on_touch_up=lambda instance, touch: mw.set_trajectory_length(instance))

        trajectory_layout.add_widget(trajectory_length_label)
        trajectory_layout.add_widget(trajectory_time_label)
        trajectory_layout.add_widget(trajectory_slider)

    mw.inner_trajectory_time_label = length_labels[0]
    mw.outer_trajectory_time_label = length_labels[1]
    #trajectory_length_label.text_size[0] = trajectory_length_label.size[0]


    # Кнопка центра масс
    """
    btn = Button(text="Центр масс", font_size=16)
    btn.bind(on_press=mw.draw_mass_center)
    """

    # Отображение планет
    objects = ['Центр масс', 'Солнце'] + PLANET_NAMES + ['Луна']
    layouts = list()
    object_labels = list()

    for name in objects:
        object_layout = BoxLayout(spacing=10)
        object_label = Label(text=name)
        object_checkbox = CheckBox()
        object_checkbox.name = name

        if name != "Центр масс":
            object_checkbox.active = True
        object_checkbox.bind(active=lambda instance, value: mw.set_visible(instance.name, value))

        object_layout.add_widget(object_label)
        object_layout.add_widget(object_checkbox)

        layouts.append(object_layout)
        object_labels.append(object_label)

    # Отображение подписей
    planet_names_layout = BoxLayout(spacing=10)

    planet_names_label = Label(text='Подписи небесных тел:')
    planet_names_checkbox = CheckBox()

    planet_names_checkbox.active = True
    planet_names_checkbox.bind(active=mw.set_labels)

    planet_names_layout.add_widget(planet_names_label)
    planet_names_layout.add_widget(planet_names_checkbox)

    # Красная точка в центре Солнца
    red_dot_layout = BoxLayout(spacing=10)

    red_dot_label = Label(text="Красная точка:")
    red_dot_checkbox = CheckBox()

    red_dot_checkbox.bind(active=mw.set_red_dot)

    red_dot_layout.add_widget(red_dot_label)
    red_dot_layout.add_widget(red_dot_checkbox)

    # Таблица расстояний
    planets_dists_layout = BoxLayout(spacing=10)

    planets_dists_label = Label(text="Таблица расстояний:")
    planets_dists_checkbox = CheckBox()
    planets_dists_checkbox.active = True

    planets_dists_checkbox.bind(active=mw.set_dists_table)

    planets_dists_layout.add_widget(planets_dists_label)
    planets_dists_layout.add_widget(planets_dists_checkbox)

    # Виджеты для изменения масштаба орбиты Луны
    moon_orbit_layout = BoxLayout(spacing=10)

    moon_orbit_label = Label(text="Масштаб Луны:")
    moon_orbit_scale = Label(text="50x")
    moon_orbit_slider = Slider(min=1, max=150, value=50)

    mw.moon_orbit_label = moon_orbit_scale
    moon_orbit_slider.bind(on_touch_move=lambda instance, touch: mw.set_moon_orbit_scale(instance.value))
    moon_orbit_slider.bind(on_touch_up=lambda instance, touch: mw.set_moon_orbit_scale(instance.value))    

    moon_orbit_layout.add_widget(moon_orbit_label)
    moon_orbit_layout.add_widget(moon_orbit_scale)
    moon_orbit_layout.add_widget(moon_orbit_slider)

    # Измененние масштаба
    """
    scale_layout = BoxLayout(spacing=10)
    
    scale_label = Label(text="Масштаб:")

    scale_plus_btn = Button(text="+", font_size=16)
    scale_plus_btn.bind(on_press=lambda instance: mw.rescale(instance, 1.5))

    scale_minus_btn = Button(text="-", font_size=16)
    scale_minus_btn.bind(on_press=lambda instance: mw.rescale(instance, 0.67))

    scale_layout.add_widget(scale_label)
    scale_layout.add_widget(scale_plus_btn)
    scale_layout.add_widget(scale_minus_btn)
    """

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

    # Ввод даты

    date_dropdown = DropDown()
    ad_button, bc_button = Button(text="A.D.", size_hint_y=None), Button(text="B.C.", size_hint_y=None)
    
    ad_button.bind(on_release=lambda btn: date_dropdown.select(btn.text))
    bc_button.bind(on_release=lambda btn: date_dropdown.select(btn.text))

    date_dropdown.add_widget(bc_button)
    date_dropdown.add_widget(ad_button)

    date_dropdown_button = Button(text='A.D.')
    date_dropdown_button.bind(on_release=date_dropdown.open)
    date_dropdown.bind(on_select=lambda instance, x: setattr(date_dropdown_button, 'text', x))

    date_enter_label = Label(text="Ввод даты в формате: B.C./A.D. год-номер месяца-номер дня", halign='center')

    date_enter_layout = BoxLayout(spacing=10)
    date_input = TextInput()
    date_enter_button = Button(text="Установить дату", font_size=16)
    date_enter_button.bind(on_release=lambda btn: mw.set_date(date_input, pause_btn, date_dropdown_button))
    
    date_enter_layout.add_widget(date_dropdown_button)
    date_enter_layout.add_widget(date_input)
    date_enter_layout.add_widget(date_enter_button)

    # Пауза
    pause_btn = Button(text="Пауза", font_size=16)
    pause_btn.bind(on_press=mw.pause)
    mw.pause_btn = pause_btn

    # Метка с датой
    date_label = Label(font_size=30)

    left_space.add_widget(theme_layout)
    left_space.add_widget(origin_layout)
    left_space.add_widget(trajectory_all_label)
    left_space.add_widget(trajectory_inner_layout)
    left_space.add_widget(trajectory_outer_layout)
    #left_space.add_widget(btn)
    for layout in layouts:
        left_space.add_widget(layout)
    left_space.add_widget(planet_names_layout)
    left_space.add_widget(red_dot_layout)
    left_space.add_widget(planets_dists_layout)
    left_space.add_widget(moon_orbit_layout)
    #left_space.add_widget(scale_layout)
    left_space.add_widget(speed_layout)
    left_space.add_widget(pause_btn)
    left_space.add_widget(date_enter_label)
    left_space.add_widget(date_enter_layout)
    left_space.add_widget(date_label)

    #--------------------------------------


    control_panel.buttons += dropdown_buttons
    control_panel.buttons += origin_dropdown_buttons
    control_panel.buttons += [ad_button, bc_button, date_dropdown_button, speed_plus_btn,
                                speed_minus_btn, pause_btn, date_enter_button, add_track_button]
    control_panel.labels += object_labels
    control_panel.labels += static_labels
    control_panel.labels += length_labels
    control_panel.labels += [planets_dists_label, trajectory_all_label, trajectory_length_label, trajectory_time_label, planet_names_label, origin_label, track_label, speed_label, date_label, theme_label, moon_orbit_label, moon_orbit_scale, red_dot_label, date_enter_label]

    Clock.schedule_interval(mw.update, 1.0/config.FPS)
    update_label_date = lambda x: mw.refresh_date(date_label)
    Clock.schedule_interval(update_label_date, 1.0/config.DATE_LABEL_REFRESH_RATE)

    Clock.schedule_once(lambda dt: change_color('Vintage NASA Blueprint'), 0.1)

def get_dist(firstx, firsty, secondx, secondy):
    return math.sqrt((firstx - secondx) ** 2 + (firsty - secondy) ** 2)


