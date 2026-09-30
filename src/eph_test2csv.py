import pandas as pd
import io
import os
from tqdm import tqdm
from consts import *
from kepler_planet import KeplerPlanet
from skyfield.api import load

ts = load.timescale()

def convert_date(date):
    monthes = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    year = int(date[:4])
    month_str = date[5:8]
    month = monthes.index(month_str) + 1
    day = int(date[9:11])

    return year, month, day


def get_planet_df(planet):
    csv_folder = "..\\csv\\ellipse_verify"
    filename = planet + ".txt"
    path = os.path.join(csv_folder, filename)

    with open(path, "r") as f:
        content = f.read()

    start = content.find("$$SOE")
    end = content.find("$$EOE")

    content = content[(start + 5):end]
    df = pd.read_csv(io.StringIO(content), sep=',', names=["date", "none1", "none2", "r", "dr", "ObsEcLon", "ObsEcLat", "Tru_Anom", "none3"])

    df = df.drop(columns=["none1", "none2", "none3", "dr", "Tru_Anom"])
    df['planet'] = planet
    df.insert(0, 'planet', df.pop('planet'))

    return df

planet_names = ["mercury", "venus", "earth", "mars", "jupiter", "saturn", "uranus", "neptune"]
dfs = list()

planets = list()
for i in range(len(planet_names)):
    kepler_planet = KeplerPlanet(PLANET_NAMES[i].lower(), MASSES[i], PERIODS[i], 
        ANGLES[i], PERIHELION[i], ECCENTRICITIES[i], RADIUSES[i], None, None, None)
    planets.append(kepler_planet)

#planets[-3].orbit_data = SATURN_DATA

for name in tqdm(planet_names):
    df = get_planet_df(name.lower())
    dfs.append(df)

ref = pd.concat(dfs, ignore_index=True)

r_gen, phita_gen = list(), list()

for i in range(len(ref)):
    row = ref.iloc[i, :]
    planet = row['planet']
    year, month, day = convert_date(row['date'].strip())
    if year < 2000 or year > 2100:
        r_gen.append(-1)
        phita_gen.append(-1)
        continue
    date = ts.tt(year, month, day, 0, 0)

    planet = planets[planet_names.index(planet)]
    planet.update_pos(date)
    r, phita = planet.get_planet_data()
    
    r_gen.append(r)
    phita_gen.append(phita)


    if i % 10000 == 0:
        print(i)



ref['r_gen'] = r_gen
ref['phita_gen'] = phita_gen
ref.to_csv("output.csv", index=False)

