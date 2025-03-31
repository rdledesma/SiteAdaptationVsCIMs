import pandas as pd
import matplotlib.pyplot as plt
from Geo import Geo
from Sites import Site
from glob import glob
import numpy as np
from datetime import timedelta
site = Site('LQ')

offsat = np.round((90 -site.lat)/18)
files = glob('lq/cmi/*csv', recursive=True)

d = pd.concat([pd.read_csv(x)  for x in files])
d['date'] = pd.to_datetime(d.date) + timedelta(minutes=offsat)
d['date'] = d['date'].dt.floor('Min')


d21 = d[d.date.dt.year.isin([2021, 2022])].drop_duplicates(subset=['date'])
d22 = d[d.date.dt.year.isin([2022])].drop_duplicates(subset=['date'])
d23 = d[d.date.dt.year.isin([2023])].drop_duplicates(subset=['date'])



d = pd.concat([d21,d22, d23])
plt.figure()
plt.plot(d21.date, d21.cmi.values)

dates = pd.date_range(start="2021/01/01 00:00", 
                            end="2023/12/31 23:59", 
                            freq = "1 min")

d = (d.set_index('date')
      .reindex(dates)
      .rename_axis(['date'])
      #.fillna(0)
      .reset_index())



dfGeo = Geo(
    range_dates = dates + timedelta(minutes=0.5),
    lat=site.lat, 
    long=site.long,
    gmt = 0,
    alt = site.alt,
    beta=0).df


d.columns =  ['date', 'FR', 'FR1', 'FR2', 'FR3', 'FR4', 'FR5', 
              'FR6', 'FR7', 'FR8', 'FR9', 'FR10', 'FR11', 'FR12', 'FR13', 'FR14', 'FR15',
       'FR16', 'FR17', 'FR18', 'FR19', 'FR20', 'FR30', 'FR40', 'FR50',
       'FR60', 'FR70', 'FR80', 'FR90', 'FR100']
d['ctz'] = dfGeo.CTZ

for x in ['FR', 'FR1', 'FR2', 'FR3', 'FR4', 'FR5', 
              'FR6', 'FR7', 'FR8', 'FR9', 'FR10', 'FR11', 'FR12', 'FR13', 'FR14', 'FR15',
       'FR16', 'FR17', 'FR18', 'FR19', 'FR20', 'FR30', 'FR40', 'FR50',
       'FR60', 'FR70', 'FR80', 'FR90', 'FR100']:
    
    d[f'RP{x[2:]}'] = (d[x]/d.ctz).interpolate(limit=60)  
    d[f'RP{x[2:]}'] = np.where(d.ctz<0, 0, d[f'RP{x[2:]}'])
    d[f'RP{x[2:]}'] = np.where(d[f'RP{x[2:]}']<0, 0, d[f'RP{x[2:]}'])
    d[f'RP{x[2:]}'] = np.where(d[f'RP{x[2:]}']>100, np.nan, d[f'RP{x[2:]}'])
    d[f'RP{x[2:]}'] = d[f'RP{x[2:]}'].interpolate(limit=30)



d = d[['date', 'ctz', 'FR', 'FR1', 'FR2', 'FR3', 'FR4', 'FR5', 
              'FR6', 'FR7', 'FR8', 'FR9', 'FR10', 'FR11', 'FR12', 'FR13', 'FR14', 'FR15',
       'FR16', 'FR17', 'FR18', 'FR19', 'FR20', 'FR30', 'FR40', 'FR50',
       'FR60', 'FR70', 'FR80', 'FR90', 'FR100']]

d = d.resample(
                        '10 min', 
                        on='date', 
                        ).mean().reset_index()


d.to_csv('lq/cmi/FR.csv', index=False)

# nsrdb = pd.read_csv('yu/nsrdb/6876993_-23.64_-64.47_2018.csv', header=2)
# nsrdb['date'] = pd.to_datetime(nsrdb[['Year', 'Month', 'Day', 'Hour', 'Minute']])

# nsrdb = (nsrdb.set_index('date')
#       .reindex(d.date)
#       .rename_axis(['date'])
#       #.fillna(0)
#       .reset_index())


# d[['nsrbd']]