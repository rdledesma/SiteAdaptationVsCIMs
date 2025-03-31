import pandas as pd
from Geo import Geo
import joblib 
import tensorflow as tf
from Sites import Site
import Metrics as ms



site = Site('YU')

d = pd.read_csv('yu/test/test.csv')
d['date'] = pd.to_datetime(d.date)
scaler = joblib.load('yu/scaler.pkl')


model = tf.keras.models.load_model('yu/model_yu.keras')


dfGeo = Geo(d.date, site.lat, site.long, 
            gmt=0, 
            alt=site.alt, 
            beta=0).df

d['sza'] = dfGeo.SZA
d['CTZ'] = dfGeo.CTZ
d['argp'] = dfGeo.GHIargp2

d= d[d.date.dt.year == 2017]


X = d[['FR', 'sza', 'CTZ', 'argp']]


Xtrain = pd.read_csv('yu/test/train.csv', usecols=[ 'FR', 'sza', 'CTZ', 'argp'])


X_scaled = scaler.transform(X)



X_train_scaled = scaler.transform(Xtrain)
Xtrain['Adap'] = model.predict(X_train_scaled).flatten()



d['Adap'] = model.predict(X_scaled).flatten()

ms.rrmsd(d.ghi, d.gcim)
ms.rrmsd(d.ghi, d.Adap)
    

import matplotlib.pyplot as plt

plt.figure()
plt.plot(d.date, d.ghi, '-')
plt.plot(d.date, d.gcim, '-')
plt.plot(d.date, d.Adap, '-')

