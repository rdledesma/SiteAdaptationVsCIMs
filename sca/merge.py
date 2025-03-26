import pandas as pd
import glob
from Sites import Site
import matplotlib.pyplot as plt
from Geo import Geo
import numpy as np
from NollasQC import QC

site = Site('SCA')
d = pd.read_csv('sca/data/sca.csv')

d['date'] = pd.to_datetime(d.date)

g = Geo(range_dates=d.date,
        lat=site.lat, 
        long=site.long, 
        gmt=0, alt=site.alt, beta=0).df


plt.figure()
plt.plot(g.SZA,d.ghi,'.', ms=0.1)




plt.figure()
sc = plt.scatter(d[g.SZA<80].date.dt.date, 
                  g[g.SZA<80].date.dt.hour + g[g.SZA<80].date.dt.minute/60  , 
                  c=d[g.SZA<80].ghi, 
                  cmap="plasma")
plt.ylabel("\u03B3$_s$")
plt.xlabel("\u03B1s$_s$")
clb = plt.colorbar(sc)
clb.ax.set_ylabel('GHI $Wm^2$ ')
plt.show()



# plt.figure()
# plt.plot(d.date, d.ghi)



d['hs'] = g.HS.values
d['ghi'] = np.where((d.date.dt.month == 10) & (g.HR>20.5), np.nan, d.ghi)



d['SZA'] = g.SZA.values
d['alphaS'] = g.alphaS.values
d['TZ'] = g.TZ.values
d['CTZ'] = g.CTZ.values
d['TOA'] = g.TOA.values


QC(d)


d['ghi'] = np.where(d.Acepted, d.ghi, np.nan)



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



d10.to_csv('sca/meas/sca_10.csv', index=False)
d15.to_csv('sca/meas/sca_15.csv', index=False)
d60.to_csv('sca/meas/sca_60.csv', index=False)

