import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
from NollasQC import QC
from Sites import Site
from Geo import Geo

files = glob.glob('lq/data/*csv', recursive=True)
site = Site("LQ")



d = pd.concat([pd.read_csv(x, usecols=[4,3])  for x in files])
d.columns = ['ghi','date']
d = d[['date','ghi']]

d['date'] = pd.to_datetime(d.date)
d = d.sort_values(by=['date'])

dates = pd.date_range(
    start="2020/01/01 00:00", end="2023/12/31 23:59", freq="1min")

d = d.drop_duplicates('date')


d = d.set_index('date').reindex(dates).rename_axis(['date']).reset_index()

d['ghi'] = np.where((d.date.dt.date >= datetime.date(2022,10,2)) & (d.date.dt.date <= datetime.date(2022,10,26)), np.nan, d.ghi)

d['ghi'] = np.where((d.date.dt.date == datetime.date(2022,3,17)), np.nan, d.ghi)
d['ghi'] = np.where((d.date.dt.date == datetime.date(2023,2,13)), np.nan, d.ghi)

d['ghi'] = np.where((d.date.dt.date == datetime.date(2023,1,5)), np.nan, d.ghi)
d['ghi'] = np.where((d.date.dt.date == datetime.date(2023,1,15)), np.nan, d.ghi)
d['ghi'] = np.where((d.date.dt.date == datetime.date(2023,1,16)), np.nan, d.ghi)
d['ghi'] = np.where((d.date.dt.date == datetime.date(2023,1,17)), np.nan, d.ghi)
d['ghi'] = np.where((d.date.dt.date == datetime.date(2023,1,30)), np.nan, d.ghi)
d['ghi'] = np.where((d.date.dt.date == datetime.date(2023,1,31)), np.nan, d.ghi)
d['ghi'] = np.where((d.date.dt.date == datetime.date(2023,2,1)), np.nan, d.ghi)
d['ghi'] = np.where((d.date.dt.date == datetime.date(2023,3,5)), np.nan, d.ghi)
d['ghi'] = np.where((d.date.dt.date == datetime.date(2023,5,13)), np.nan, d.ghi)
d['ghi'] = np.where((d.date.dt.date == datetime.date(2023,6,22)), np.nan, d.ghi)



g = Geo(d.date,
        lat=site.lat, 
        long=site.long, 
        gmt=0, alt=site.alt, beta=0).df

d['SZA'] = g.SZA.values
d['TZ'] = g.TZ.values
d['CTZ'] = g.CTZ.values
d['TOA'] = g.TOA.values

d['ghi'] = np.where( d.CTZ<0, np.nan, d.ghi)

d['ghi'] = np.where( d.ghi/d.TOA<0, np.nan, d.ghi)


QC(d)


d['ghi'] = np.where( d.Acepted, d.ghi, np.nan)






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



d10.to_csv('lq/meas/lq_10.csv', index=False)
d15.to_csv('lq/meas/lq_15.csv', index=False)
d60.to_csv('lq/meas/lq_60.csv', index=False)
