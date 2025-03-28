import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
from NollasQC import QC
from Sites import Site
from Geo import Geo
from datetime import timedelta
from scipy.optimize import curve_fit
import Metrics as ms

site = Site("YU")


d = pd.read_csv('yu/cmi/FR.csv')
d = d.dropna()
d['date'] = pd.to_datetime(d.date)


plt.plot(d.date, d.FR)


d = d[d.ctz>0.1217]



window_size = 300
min_count = 20

# Función para calcular el promedio de los 20 valores mínimos
def mean_of_min_20(x):
    return x.nsmallest(min_count).mean()

# Aplicar la función en una ventana móvil centrada
result = d['FR16'].rolling(window=window_size, center=True).apply(mean_of_min_20, raw=False)

 
d['r0'] = result
d['n'] = (d.FR16 - d.r0) / (80 - d.r0) 
d['n'] = np.where(d['n'] > 0.9, 0.9, d.n)
d['n'] = np.where(d['n'] < 0, 0, d.n)
d = d.dropna()


dtrain = d[d.date.dt.year == 2018]
dtest = d[d.date.dt.year != 2018]

dfGeo = Geo(
    range_dates = dtrain.date + timedelta(minutes=5),
    lat=site.lat, 
    long=site.long,
    gmt = 0,
    alt = site.alt,
    beta=0).df



dtrain['ghicc'] = dfGeo.GHIargp2.values


dfGeoTest = Geo(
    range_dates = dtest.date + timedelta(minutes=5),
    lat=site.lat, 
    long=site.long,
    gmt = 0,
    alt = site.alt,
    beta=0).df

dtest['ghicc'] = dfGeoTest.GHIargp2.values



meas = pd.read_csv('yu/meas/yu_15.csv')
meas['date'] = pd.to_datetime(meas.date)


measTrain = (meas.set_index('date')
      .reindex(dtrain.date)
      .rename_axis(['date'])
      #.fillna(0)
      .reset_index())


dtrain['ghi'] = measTrain.ghi.values
dtrain = dtrain.dropna()

measTest= (meas.set_index('date')
      .reindex(dtest.date)
      .rename_axis(['date'])
      #.fillna(0)
      .reset_index())

dtest['ghi'] = measTest.ghi.values
dtest = dtest.dropna()



def ghiCMI_func(x, a, b):
    ghicc, n = x
    return ghicc * (a *  n + b)


# Ajustar la función usando curve_fit
popt, pcov = curve_fit(ghiCMI_func, (dtrain.ghicc, dtrain.n), dtrain.ghi)

# Obtener los valores óptimos de 'a' y 'b'
a_opt,b_opt  = popt


dtest['gcim'] = dtest.ghicc * (a_opt * dtest.n + b_opt)



plt.figure()
plt.plot(dtest.date, dtest.ghi)
plt.plot(dtest.date, dtest.gcim)
ms.rrmsd(dtest.ghi, dtest.gcim)


# s = dtest.resample('15 min',on='date').mean()

# s =s.dropna()


# ms.rmbe(s.ghi, s.gcim)




# nsrdb = pd.read_csv('yu/nsrdb/6876993_-23.64_-64.47_2018.csv', header=2)
