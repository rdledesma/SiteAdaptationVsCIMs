import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta
from Geo import Geo
import numpy as np
from NollasQC import QC

d = pd.read_csv('measured/ghi_sla_2024.csv')
d.columns = ['date','ghi']

d['date'] = pd.to_datetime(d.date) + timedelta(hours=3)


dates = pd.date_range(
    start="2024/01/01 00:00",
    end="2024/12/31 23:59",
    freq="1min")

g = Geo(
        dates,
        lat=-24.7288, 
        long=-65.4095, 
        gmt = 0,
        alt = 3355,
        beta=0).df

d = d.set_index('date').reindex(g.date).rename_axis(['date']).reset_index()

d['sza'] = g.SZA
d['ghicc'] = g.GHIargp2
d['ghi'] = np.where(d.sza>=90, np.nan, d.ghi)

import datetime

d['ghi'] = np.where(d.date.dt.date== datetime.date(2024,5,7) , np.nan, d.ghi)
d['ghi'] = np.where(d.date.dt.date== datetime.date(2024,5,20) , np.nan, d.ghi)
d['ghi'] = np.where(d.date.dt.date== datetime.date(2024,5,21) , np.nan, d.ghi)
d['ghi'] = np.where(d.date.dt.date== datetime.date(2024,12,5) , np.nan, d.ghi)
d['ghi'] = np.where(d.date.dt.date== datetime.date(2024,12,9) , np.nan, d.ghi)

d['ghi'] = np.where(d.ghi<0 , np.nan, d.ghi)
d['SZA'] = d.sza
d['CTZ'] = g.CTZ
d['TZ'] = g.TZ
d['TOA'] = g.TOA
d['a'] = g.alphaS
QC(d)



d['ghi'] = np.where(d.Acepted ,  d.ghi, np.nan)

d['ghi'] = np.where(d.a>10 ,  d.ghi, np.nan)


d['GHIargp'] = g.GHIargp2

s = d[['date','SZA','ghi']]




