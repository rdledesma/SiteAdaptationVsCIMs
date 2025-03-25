import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
from NollasQC import QC
from Sites import Site
from Geo import Geo
import glob
from datetime import timedelta

d = pd.read_csv('ero/data/ero.csv')
d['date'] = pd.to_datetime(d.date) + timedelta(minutes = 180)

d = d[d.date.dt.date > datetime.date(2014,8,15)]

site = Site('ERO')
plt.figure()
plt.plot(d.date, d.ghi)
# plt.plot(d.date, d.TOA)

d['ghi'] = np.where(d.date.dt.date == datetime.date(2018, 11, 2), np.nan, d['ghi'])
d['ghi'] = np.where(d.date.dt.date == datetime.date(2017, 12, 9), np.nan, d['ghi'])
d['ghi'] = np.where(d.date.dt.date == datetime.date(2017, 12, 10), np.nan, d['ghi'])
d['ghi'] = np.where(d.date.dt.date == datetime.date(2017, 12, 11), np.nan, d['ghi'])
d['ghi'] = np.where(d.date.dt.date == datetime.date(2018, 1, 31), np.nan, d['ghi'])

d['ghi'] = np.where(d.date.dt.date == datetime.date(2015, 10, 16), np.nan, d['ghi'])
d['ghi'] = np.where(d.date.dt.date == datetime.date(2017, 5, 31), np.nan, d['ghi'])
#d['ghi'] = np.where(d.date.dt.date == datetime.date(2017, 5, 16), np.nan, d['ghi'])

#d['ghi'] = np.where(d.date.dt.date == datetime.date(2017, 4, 16), np.nan, d['ghi'])



d['ghi'] = np.where((d.date.dt.date >= datetime.date(2018, 3, 30)) & (d.date.dt.date <= datetime.date(2018, 4, 3)), np.nan, d['ghi'])
d['ghi'] = np.where((d.date.dt.date >= datetime.date(2018, 12, 12)) & (d.date.dt.date <= datetime.date(2018, 12, 12)), np.nan, d['ghi'])

d['ghi'] = np.where(d.date.dt.date == datetime.date(2024, 12, 10), np.nan, d.ghi)

plt.figure()
plt.plot(d.date, d.ghi)
plt.show()

d = d.dropna()
    
g = Geo(d.date, lat=site.lat, long=site.long, gmt=0, alt=site.alt, beta=0).df.interpolate() 

import math 
d['SZA'] = g.SZA.values

d['alphaS'] = g.alphaS.values
d['TZ'] = g.TZ.values
d['CTZ'] = g.CTZ.values
d['TOA'] = g.TOA.values
d['Ys'] = g['Ys'].apply(math.degrees)
# d['ghi'] = np.where(g.SZA<90,d['ghi'], np.nan)


d = d[d.CTZ>0]
d = d[d.alphaS>12]
d = d[d.ghi>5]

plt.figure()
plt.plot(d.SZA, d.ghi,'.', ms=0.025)


# d['ghi'] = np.where(((d.ghi<30) & (d.SZA>77)), np.nan, d.ghi)

# d['ghi'] = np.where(((d.ghi<50) & (d.SZA>78)), np.nan, d.ghi)




import math
plt.figure()

sc = plt.scatter(d.date.dt.date, 
                 d.date.dt.hour + d.date.dt.minute / 60  , 
                 c=d.ghi, 
                 cmap="plasma")
plt.ylabel("\u03B3$_s$")
plt.xlabel("\u03B1s$_s$")
clb = plt.colorbar(sc)
clb.ax.set_ylabel('GHI $Wm^2$ ')
plt.show()


#plt.plot(d[d.date.dt.year == 2024].SZA, d[d.date.dt.year == 2024].ghi,'.', ms=1)

d['ghi'] = np.where((d.date.dt.dayofyear<50) & (d.date.dt.time > datetime.time(20,20)) & (d.date.dt.time < datetime.time(20,50)), np.nan, d.ghi) 
d['ghi'] = np.where(d.date.dt.month.isin([5,6,7]) & (d.SZA>75), np.nan, d.ghi )


s = d[d.date.dt.month.isin([5,6,7])]

import math
plt.figure()

sc = plt.scatter(d.date.dt.date, 
                 d.CTZ, 
                 c=d.ghi, 
                 cmap="plasma")
plt.ylabel("\u03B3$_s$")
plt.xlabel("\u03B1s$_s$")
clb = plt.colorbar(sc)
clb.ax.set_ylabel('GHI $Wm^2$ ')
plt.show()



QC(d)

d['ghi'] = np.where(d.Acepted, d.ghi, np.nan)
d['ghi'] = np.where(d.ghi<d.TOA, d.ghi, np.nan)



plt.figure()
plt.plot(d.SZA, d.ghi,'.', ms=0.1)

d = d.dropna()

d = d[['date','ghi']]



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

# plt.figure()
# plt.plot(d15.date, d15.ghi)
# plt.plot(d15.date, d15.ghi_fil)


cuentas60 = d.resample( '60 min',on='date').ghi.count()
d60 = d.resample( '60 min',on='date').ghi.mean().reset_index()
d60['cuentas'] = cuentas60.values
d60['ghi_fil'] = np.where(d60.cuentas>=40, d60.ghi, np.nan)

# plt.figure()
# plt.plot(d60.date, d60.ghi_fil)


d10 = d10[['date','ghi_fil']]
d10.columns = ['date','ghi']

d15 = d15[['date','ghi_fil']]
d15.columns = ['date','ghi']

d60 = d60[['date','ghi_fil']]
d60.columns = ['date','ghi']



d10.to_csv('ero/meas/ero_10.csv', index=False)
d15.to_csv('ero/meas/ero_15.csv', index=False)
d60.to_csv('ero/meas/ero_60.csv', index=False)


