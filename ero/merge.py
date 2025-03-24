import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
from NollasQC import QC
from Sites import Site
from Geo import Geo
import glob
from datetime import timedelta


files = glob.glob('ero/data/*csv', recursive=True)
site = Site("ERO")

d = pd.concat([pd.read_csv(x)  for x in files])
d.columns = ['date','ghi']


d['date'] = pd.to_datetime(d.date) + timedelta(minutes = 180)
d = d.sort_values(by=['date'])


d.to_csv('ero/data/ero.csv', index=False)

plt.figure()
plt.plot(d.date, d.ghi)
plt.plot(d.date, d.TOA)


#d['ghi'] = np.where((d.date.dt.date > datetime.date(2018, 1, 5)) & (d.date.dt.date <= datetime.date(2018, 1, 31)), np.nan, d['ghi'])

#d['ghi'] = np.where((d.date.dt.date > datetime.date(2018, 2, 17)) & (d.date.dt.date <= datetime.date(2018, 3, 12)), np.nan, d['ghi'])
#d['ghi'] = np.where((d.date.dt.date >= datetime.date(2018, 4, 9)) & (d.date.dt.date <= datetime.date(2018, 5, 3)), np.nan, d['ghi'])
    
g = Geo(d.date, lat=site.lat, long=site.long, gmt=0, alt=site.alt, beta=0).df 


plt.figure()
plt.plot(d.date, d.ghi)

d['ghi'] = np.where(g.SZA<90,d['ghi'], np.nan)

d['SZA'] = g.SZA.values


plt.figure()
# plt.plot(d.SZA, d.ghi,'.', ms=1)
plt.plot(d[d.date.dt.year == 2024].SZA, d[d.date.dt.year == 2024].ghi,'.', ms=1)


d['TZ'] = g.TZ.values

d['CTZ'] = g.CTZ.values
d['TOA'] = g.TOA.values

QC(d)

d['ghi'] = np.where(d.Acepted, d.ghi, np.nan)
d['ghi'] = np.where(d.ghi<d.TOA, d.ghi, np.nan)



plt.figure()
plt.plot(d.SZA, d.ghi,'.', ms=1)




cuentas10 = d.resample( '10 min',on='date').ghi.count()
d10 = d.resample( '10 min',on='date').ghi.mean().reset_index()
d10['cuentas'] = cuentas10.values
d10['ghi_fil'] = np.where(d10.cuentas>=6, d10.ghi, np.nan)

plt.figure()
plt.plot(d10.date, d10.ghi)
plt.plot(d10.date, d10.ghi_fil)



cuentas15 = d.resample( '15 min',on='date').ghi.count()
d15 = d.resample( '15 min',on='date').ghi.mean().reset_index()
d15['cuentas'] = cuentas15.values
d15['ghi_fil'] = np.where(d15.cuentas>=10, d15.ghi, np.nan)

plt.figure()
plt.plot(d15.date, d15.ghi)
plt.plot(d15.date, d15.ghi_fil)


cuentas60 = d.resample( '60 min',on='date').ghi.count()
d60 = d.resample( '60 min',on='date').ghi.mean().reset_index()
d60['cuentas'] = cuentas60.values
d60['ghi_fil'] = np.where(d60.cuentas>=40, d60.ghi, np.nan)

plt.figure()
plt.plot(d60.date, d60.ghi_fil)


d10 = d10[['date','ghi_fil']]
d10.columns = ['date','ghi']

d15 = d15[['date','ghi_fil']]
d15.columns = ['date','ghi']

d60 = d60[['date','ghi_fil']]
d60.columns = ['date','ghi']



d10.to_csv('yu/yu_10.csv', index=False)
d15.to_csv('yu/yu_15.csv', index=False)
d60.to_csv('yu/yu_60.csv', index=False)
