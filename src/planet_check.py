from kepler_planet import KeplerPlanet
from consts import *
from skyfield.api import load
import pandas as pd
import os
import io
from moon import Moon


def convert_date(date):
    monthes = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    year = int(date[:4])
    month_str = date[5:8]
    month = monthes.index(month_str) + 1
    day = int(date[9:11])
    hour = int(date[12:14])
    minutes = int(date[15:17])

    return year, month, day, hour, minutes

def get_planet_df(planet):
    csv_folder = "..\\csv\\ellipse_verify"
    filename = planet + ".txt"
    path = os.path.join(csv_folder, filename)
    path = "..\\csv\\moon_range.txt"

    with open(path, "r") as f:
        content = f.read()

    start = content.find("$$SOE")
    end = content.find("$$EOE")

    content = content[(start + 5):end]
    df = pd.read_csv(io.StringIO(content), sep=',', names=["date", "none1", "none2", "delta", "deldot", "ObsEcLon", "ObsEcLat", "none3"])

    df = df.drop(columns=["none1", "none2", "none3", "ObsEcLat", "deldot"])
    df['planet'] = planet
    df.insert(0, 'planet', df.pop('planet'))

    return df

ts = load.timescale()
moon = Moon()
df = get_planet_df("moon")

phita_gen = list()
r_gen = list()
print(len(df))

for i in range(len(df)):
    row = df.iloc[i, :]
    planet = row['planet']
    year, month, day, hour, minutes = convert_date(row['date'].strip())
    date = ts.tt(year, month, day, hour, minutes, 0)

    r, phita = moon.get_pos(date)
    
    phita_gen.append(phita)
    r_gen.append(r)

    if i % 10000 == 0:
        print(i)

df['phita_gen'] = phita_gen
df['r_gen'] = r_gen
df.to_csv("output.csv", index=False)





