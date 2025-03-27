import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
from NollasQC import QC
from Sites import Site
from Geo import Geo

files = glob.glob('lq/nsrdb/*csv', recursive=True)
site = Site("LQ")

d = pd.concat([pd.read_csv(x, header=2)  for x in files])
d['date'] = pd.to_datetime(d[['Year', 'Month', 'Day', 'Hour', 'Minute']])

d = d[['date','GHI']]

d.columns = ['date','nsrdb']
d['date'] = pd.to_datetime(d.date)
d = d.sort_values(by=['date'])

dates = pd.date_range(
    start="2020/01/01 00:00", end="2023/12/31 23:59", freq="10min")

d = d.drop_duplicates('date')


d = d.set_index('date').reindex(dates).rename_axis(['date']).reset_index()



meas = pd.read_csv('lq/meas/lq_10.csv')
meas['date'] = pd.to_datetime(meas.date)



plt.figure()
plt.plot(meas.date, meas.ghi)
plt.plot(d.date, d.nsrdb)




# cuentas60 = d.resample( '60 min',on='date').ghi.count()
# d60 = d.resample( '60 min',on='date').ghi.mean().reset_index()
# d60['cuentas'] = cuentas60.values
# d60['ghi_fil'] = np.where(d60.cuentas>=40, d60.ghi, np.nan)

# plt.figure()
# plt.plot(d60.date, d60.ghi_fil)



# d10 = d10[['date','ghi_fil']]
# d10.columns = ['date','ghi']

# d15 = d15[['date','ghi_fil']]
# d15.columns = ['date','ghi']

# d60 = d60[['date','ghi_fil']]
# d60.columns = ['date','ghi']



# d10.to_csv('lq/meas/lq_10.csv', index=False)
# d15.to_csv('lq/meas/lq_15.csv', index=False)
# d60.to_csv('lq/meas/lq_60.csv', index=False)
