import datetime as dt



# Константы

# --- Радиусы орбит [а. е.] ---
RADIUSES = [
	0.387, # Меркурий
	0.723, # Венера
	1., # Земля
	1.524, # Марс
	5.2, # Юпитер
	9.58, # Сатурн
	19.19, # Уран
	30.1, # Нептун
	#39.48 # Плутон
]

#-----------------------------


# --- Период вращения вокруг Солнца [земной день] ---
PERIODS = [
	dt.timedelta(days=87, hours=23, minutes=15, seconds=43, microseconds=804800), # Меркурий
	dt.timedelta(days=224, hours=16, minutes=49, seconds=9, microseconds=120000), # Венера
	dt.timedelta(days=365, hours=6, minutes=9, seconds=9, microseconds=504000), # Земля
	dt.timedelta(days=686, hours=23, minutes=30, seconds=37, microseconds=440000), # Марс
	dt.timedelta(days=4332, hours=19, minutes=40, seconds=56, microseconds=640000), # Юпитер
	dt.timedelta(days=10755, hours=16, minutes=46, seconds=33, microseconds=600000), # Сатурн
	dt.timedelta(days=30687, hours=3, minutes=40, seconds=19, microseconds=200000), # Уран
	dt.timedelta(days=60190, hours=0, minutes=43, seconds=12, microseconds=0), # Нептун
	#dt.timedelta(days=90553, hours=0, minutes=28, seconds=48, microseconds=0) # Плутон
]

#------------------------------


# --- Масса планет [10^25 kg] ---
MASSES = [
	0.0033, # Меркурий
	0.487, # Венера
	0.597, # Земля
	0.064, # Марс
	189.813, # Юпитер
	56.846, # Сатурн
	8.681, # Уран
	10.24, # Нептун
	#0.001 # Плутон	
]

#-------------------------------

#-------------------------------
PLANET_NAMES = [
	'Меркурий',
	'Венера',
	'Земля',
	'Марс',
	'Юпитер',
	'Сатурн',
	'Уран',
	'Нептун'
]
#-------------------------------

#-------------------------------
PLANET_NAMES_ENG = planet_names = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]

#-------------------------------
