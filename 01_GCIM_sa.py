import os 
cwd = os.getcwd()
import sys
sys.path.append('/home/dario/geers/GCIMvsSA')

import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import Metrics  as mts


sa = pd.read_csv('RP/sa/10.csv')
sa['date'] = pd.to_datetime(sa.date)

sa = sa.resample(
                    f'15 min', 
                    on='date', 
                    ).mean().reset_index()

rpMonths = []




for m in sa.date.dt.month.unique():
    d = sa[sa.date.dt.month == m]
    d = d[d.ctz>0.12]
    minRp = d.RP10.to_list()
    minRp.sort()
    rpMonths.append(np.mean(minRp[1:5]))


meas = pd.read_csv('measured/sa_15.csv')
meas['date'] = pd.to_datetime(meas.date)



meas = (meas.set_index('date')
      .reindex(sa.date)
      .rename_axis(['date'])
      #.fillna(0)
      .reset_index())

meas['RP'] = sa.RP10

for x in range(1,10):
    meas[f'RP{x}'] = sa[f'RP{x}'] 





meas['R0'] = None

for i, m in enumerate(rpMonths):
    meas['R0'] = np.where(meas.date.dt.month == i+1, m, meas.R0)



plt.figure()
plt.plot(meas.date, meas.R0 , label="Meas")
plt.show()


meas['n'] = (meas.RP - meas.R0) / (85 - meas.R0)
meas['n'] = np.where(meas['n'] > 1, 1, meas.n)
meas['n'] = np.where(meas['n'] < 0, 0, meas.n)



cams = pd.read_csv('cams/sa_15.csv', sep=";", header=42)
cams['date'] = [x[:19] for x in cams.iloc[:,0].to_list()]
cams = cams[['date','GHI', 'Clear sky GHI']]
cams['date'] = pd.to_datetime(cams.date)
cams = cams[cams.date.dt.year == 2023]


meas['GHI'] = cams['GHI'] * 4
meas['GHIcc'] = cams['Clear sky GHI'] * 4

meas = meas[meas.sza<85]

plt.figure()
plt.plot(meas.date, meas.ghi)
plt.plot(meas.date, meas.GHIcc)
plt.show()


meas = meas.dropna()

# Definir la función para calcular 'ghiCMI' dado 'a' y 'b'
def ghiCMI_func(x, a, b):
    GHIargp2, n = x
    return GHIargp2 * (a * (1 - n) + b)

# Ajustar la función usando curve_fit
popt, pcov = curve_fit(ghiCMI_func, (meas.GHIcc, meas.n), meas.ghi)

# Obtener los valores óptimos de 'a' y 'b'
a_opt,b_opt  = popt


meas['gcim']  = meas.GHIcc * ( a_opt * (1 - meas.n) + b_opt)



mts.rrmsd(meas.ghi, meas.GHI)
mts.rrmsd(meas.ghi, meas.gcim)


from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler



meas = meas[meas.sza<80]

scaler = MinMaxScaler()
X = meas[['GHIcc','RP']]
X = scaler.fit_transform(X)









reg = LinearRegression().fit(X, meas.ghi - meas.GHIcc)
meas['siteAdap'] = reg.predict(X) + meas.GHIcc
meas['siteAdap'] = np.where(meas['siteAdap'] < 0, 0, meas.siteAdap)


plt.figure()
#plt.plot(meas.ghi, meas.GHI,  '.',label="Meas")
plt.plot(meas.date, meas.ghi, '-', label="Meas")
plt.plot(meas.date, meas.gcim, '-',label="GCIM-2")
plt.plot(meas.date, meas.siteAdap,'-', label="SiteAdap")
plt.legend()
plt.show()


mts.rrmsd(meas.ghi, meas.GHI)
mts.rrmsd(meas.ghi, meas.gcim)
mts.rrmsd(meas.ghi, meas.siteAdap)

