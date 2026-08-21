import pandas as pd
from skyfield.api import load
import configs.config as config
from planet import Planet
import datetime as dt
from consts import *
import math
from sys import exit

ts = load.timescale()
date = ts.tt(-10, 1)
print(date.tt)
exit(0)

cur_date = ts.utc(-4999, 1, 1, 12, 0)
stop_date = ts.utc(5000, 1, 1, 12, 0)

step = dt.timedelta(days=7)

planets = list()

max_radius = max(RADIUSES)
for i in range(len(RADIUSES)):
    planet = Planet(PLANET_NAMES_ENG[i], config.ROOT_DATE, MASSES[i], RADIUSES[i], PERIODS[i], (RADIUSES[i] / max_radius),
                        None, None, config.START_POS[i])
    planets.append(planet)

planets_names, date, deg = list(), list(), list()
while cur_date < stop_date:
    for planet in planets:
        planet.update_pos(cur_date)

    for planet in planets:
        planets_names.append(planet.name)
        d = cur_date.utc_jpl()[:-12]
        if "B.C." in d:
            d = "b" + d[5:]
        else:
            d = d[5:]

        date.append(d)
        deg.append(planet.pos/math.pi * 180)

    cur_date += step
    if cur_date.utc_jpl()[:-12][-1] != '0':
        cur_date += dt.timedelta(minutes=1)
    if cur_date.utc.year % 100 == 0 and cur_date.utc.month == 1:
        print(cur_date.utc_jpl()[:-12])

print(len(planets_names), len(date), len(deg))
df = pd.DataFrame(data={'planet': planets_names, 'date': date, 'deg': deg})
df.to_csv('planets.csv')

