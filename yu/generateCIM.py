import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
from NollasQC import QC
from Sites import Site
from Geo import Geo
from datetime import timedelta

site = Site("YU")


d = pd.read_csv('yu/cmi/FR.csv')
d = d.dropna()
d['date'] = pd.to_datetime(d.date)

d = d[d.ctz>0.12]



window_size = 1800
min_count = 20

# Función para calcular el promedio de los 20 valores mínimos
def mean_of_min_20(x):
    return x.nsmallest(min_count).mean()

# Aplicar la función en una ventana móvil centrada
result = d['FR16'].rolling(window=window_size, center=True).apply(mean_of_min_20, raw=False)

 
d['r0'] = result
d['n'] = (d.FR16 - d.r0) / (80 - d.r0) 
d['n'] = np.where(d['n'] > 1, 1, d.n)
d['n'] = np.where(d['n'] < 0, 0, d.n)
d = d.dropna()


dtrain = d[d.date.dt.year == 2018]

dfGeo = Geo(
    range_dates = dtrain.date + timedelta(minutes=5),
    lat=site.lat, 
    long=site.long,
    gmt = 0,
    alt = site.alt,
    beta=0).df


dtrain['ghicc'] = dfGeo.GHIargp2.values
