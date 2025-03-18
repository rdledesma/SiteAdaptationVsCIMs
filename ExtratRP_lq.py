import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import timedelta
from Geo import Geo
from dateutil.relativedelta import relativedelta

d = pd.read_csv('CloudMoustImag/lq_cmi_2023_delta.csv')

d['date'] = pd.to_datetime(d.date)
d = d[d.date.dt.year == 2023]





offsat = np.round((90 - -24.103936)/18)


d['date'] = pd.to_datetime(d.date) + timedelta(minutes = offsat)
d['date'] = d['date'].dt.floor('Min')



dates = pd.date_range(start="2023/01/01 00:00", 
                            end="2023/12/31 23:59", 
                            freq = "1 min")

d = (d.set_index('date')
      .reindex(dates)
      .rename_axis(['date'])
      #.fillna(0)
      .reset_index())





g = Geo(range_dates = d.date + timedelta(minutes=0.5),
             lat = -22.103936,
             long = -65.599923,
             gmt = 0,
             alt = 3500,
             beta=0).df


d['ctz'] = g.CTZ.values



for x in range(1,11):
    d.iloc[:,x] = np.where(d.ctz<=0, 0, d.iloc[:,x]/d.ctz)

for x in ['cmi1', 'cmi2', 'cmi3', 'cmi4', 'cmi5', 'cmi6', 'cmi7', 'cmi8',
       'cmi9', 'cmi10']:
    d[x] = np.where((d[x]<0) | (d[x]>100), np.nan, d[x])

d = d.interpolate(limit=60)


d.columns = ['date','RP1', 'RP2', 'RP3', 'RP4', 'RP5', 'RP6', 'RP7', 'RP8',
       'RP9', 'RP10','ctz' ]

d = d.resample('10 min', on='date').mean().reset_index()


g = Geo(range_dates = d.date + timedelta(minutes=5),
             lat = -22.103936,
             long = -65.599923,
             gmt = 0,
             alt = 3500,
             beta=0).df


d['ctz'] = g.CTZ.values
d['alpha'] = g.alphaS.values
d['argp2'] = g.GHIargp2.values

d.to_csv('RP/lq/10_2023.csv', index=False)
