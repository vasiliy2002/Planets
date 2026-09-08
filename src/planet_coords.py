from astroquery.jplhorizons import Horizons
from tqdm import tqdm
import pandas as pd

def get_planet_info(start_date, stop_date, step, id):
    obj = Horizons(id=id, location='500@10',
                   epochs={'start': start_date, 'stop': stop_date,
                           'step': step})
    
    eph = obj.ephemerides(quantities=31, extra_precision=True, optional_settings={'CAL_TYPE': 'GREGORIAN'})
    df = pd.DataFrame(data={'date': eph['datetime_str'],
        'deg': eph['ObsEclLon']})
    return df


ids = ["Mercury Barycenter", "Venus Barycenter", "Earth-Moon Barycenter", "Mars Barycenter", "Jupiter Barycenter",
        "Saturn Barycenter", "Uranus Barycenter", "Neptune Barycenter"]
planet_names = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]

dates = ['B.C. 5000-Jan-01', 'B.C. 3894-Jan-13', 'B.C. 2985-Jun-06', 'B.C. 1984-Aug-03', 'B.C. 1036-Apr-18', 
            'A.D. 0025-Nov-20', 'A.D. 1036-Aug-11', 'A.D. 2007-Mar-15', 'A.D. 3012-Mar-12', 'A.D. 4025-May-08', 'A.D. 4999-Dec-26']
#start_date = 'A.D. 1800-Jan-01 12:00 UTC'
#stop_date = 'A.D. 3800-Jan-01 12:00'
step = '7d'

planets_info = pd.DataFrame()
for i, id in enumerate(tqdm(ids)):
    for j in range(len(dates)-1):
        start_date = dates[j] + " 12:00 UTC"
        stop_date = dates[j+1] + " 12:00"
        cur = get_planet_info(start_date, stop_date, step, id)
        cur['planet'] = planet_names[i]
        planets_info = pd.concat([planets_info, cur])
        print(stop_date)

planets_info.to_csv("planets2.csv")
