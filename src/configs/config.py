import datetime as dt
import math
from skyfield.api import load

ts = load.timescale()

# Конфигурационный файл

# Стартовые размеры окна [пиксели]
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500

# Ширина орбит [пиксели]
ORBIT_LINEWIDTH = 1

MASS_CENTER_SIZE = 12

# Размер планет
PLANET_SIZE = 12

# Стартовый масштаб
SCALE = 5

MIN_SCALE, MAX_SCALE = 0.05, 300

MASS_CENTER_LINEWIDTH = 1

# Стартовая частота отрисовки
FPS = 60

# Количество земных дней проходящих за секунду использования программы
TIME_SEC = dt.timedelta(days=90)

# Частота обновления надписи с текущим временем в секунду
DATE_LABEL_REFRESH_RATE = 2

START_DATE = ts.utc(0, 1, 1, 12, 0) #dt.datetime(2000, 1, 1, 12, 0)
ROOT_DATE = ts.utc(2000, 1, 1, 0, 0)

# Мультипликатор масштаба при управлении колесиком
SCROLL_SCALE_VALUE = 1.2

# Стартовые положения планет на орбитах [радианы]
START_POS = [
	(252.4046828 * math.pi / 180), # Меркурий
	(181.7880927 * math.pi / 180), # Венера
	(99.8647836 * math.pi / 180), # Земля
	(359.1297054 * math.pi / 180), # Марс
	(36.2464785 * math.pi / 180), # Юпитер
	(45.7022703 * math.pi / 180), # Сатурн
	(316.411957 * math.pi / 180), # Уран
	(303.9248499 * math.pi / 180), # Нептун
	#(250.5450920 * math.pi / 180) # Плутон
]

