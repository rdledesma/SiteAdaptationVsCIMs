import pandas as pd
from Geo import Geo
import matplotlib.pyplot as plt
from datetime import timedelta
import numpy as np

d = pd.read_csv('FR/fr_sa_2023.csv')
d['date'] = pd.to_datetime(d.date)
d = d[d.date.dt.year == 2023]



d.columns = ['date','FR1', 'FR2',
'FR3', 'FR4', 'FR5', 'FR6', 'FR7', 'FR8', 'FR9', 'FR10']



dates = pd.date_range(start="2023/01/01 00:00", 
                            end="2023/12/31 23:59", 
                            freq = "1 min")

offsat = np.round((90 - -24.7288)/18)


d['date'] = pd.to_datetime(d.date) + timedelta(minutes = offsat)
d['date'] = d['date'].dt.floor('Min')



d = (d.set_index('date')
      .reindex(dates)
      .rename_axis(['date'])
      #.fillna(0)
      .reset_index())



dfGeo = Geo(
    range_dates = dates + timedelta(minutes=0.5),
    lat=-24.7288, 
    long=-65.4095,
    gmt = 0,
    alt = 1233,
    beta=0).df

d['ctz'] = dfGeo.CTZ 


for x in ['FR1', 'FR2', 'FR3', 'FR4', 'FR5', 'FR6', 'FR7', 'FR8', 'FR9',
       'FR10']:
    
    d[f'RP{x[2:]}'] = (d[x]/d.ctz).interpolate(limit=60)  
    d[f'RP{x[2:]}'] = np.where(d.ctz<0, 0, d[f'RP{x[2:]}'])
    d[f'RP{x[2:]}'] = np.where(d[f'RP{x[2:]}']<0, 0, d[f'RP{x[2:]}'])
    d[f'RP{x[2:]}'] = np.where(d[f'RP{x[2:]}']>100, np.nan, d[f'RP{x[2:]}'])
    d[f'RP{x[2:]}'] = d[f'RP{x[2:]}'].interpolate(limit=30)
    

d = d[['date', 'ctz', 'RP1', 'RP2', 'RP3', 'RP4', 'RP5', 'RP6', 'RP7', 'RP8',
       'RP9', 'RP10']]








for x in [10,15,60]:        
    d.resample(
                        f'{x} min', 
                        on='date', 
                        ).mean().reset_index().to_csv(f'RP/sa/{x}_delta.csv', index=False)