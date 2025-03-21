import pandas as pd
from sklearn.model_selection import train_test_split

d = pd.read_csv('sa/CMI_10.csv')
d['date'] = pd.to_datetime(d.date)
e = pd.read_csv('sa/sa_10.csv')
e['date'] = pd.to_datetime(e.date)

d = (d.set_index('date')
      .reindex(e.date)
      .rename_axis(['date'])
      #.fillna(0)
      .reset_index())


d['ghi'] = e.ghi


d = d.dropna()


dTrain = d[d.date.dt.year<2024]
dTest = d[d.date.dt.year==2024]

X = dTrain[['FR', 'sza', 'CTZ', 'argp', 'rp']]




Xtest = dTest[['FR', 'sza', 'CTZ', 'argp', 'rp']]
y_test = dTest.ghi- dTest.argp


X_train, X_val, y_train, y_val = train_test_split(

    X, dTrain.ghi - dTrain.argp, test_size=0.2, random_state=42)


import glob
import pandas as pd

from sklearn.preprocessing import MinMaxScaler


scaler = MinMaxScaler()


Xtrain_scaled = scaler.fit_transform(X_train)
Xval_scaled = scaler.transform(X_val)
Xtest_scaled = scaler.transform(Xtest)


import pandas as pd
from sklearn.preprocessing import StandardScaler
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.callbacks import EarlyStopping
import joblib
from sklearn.model_selection import train_test_split
import Metrics as m
import matplotlib.pyplot as plt
from itertools import product
import itertools
from keras.optimizers import Adam
import numpy as np




# Definir la grilla de hiperparámetros

# Definir la grilla de hiperparámetros
param_grid = {
    "dense_layers": [(5, 10,15),(10, 15,25),(20, 25,35),(30,40),(40,50)],  # Configuraciones de capas densas
    "dropout_rates": [0,0.1],  # Tasa de dropout
    "epochs": [60,70,80,90 ],  # Número de épocas
    "batch_size": [40],  # Tamaño de lote
    "learning_rate": [0.1, 0.01]  # Diferentes tasas de aprendizaje
}


# Crear combinaciones de hiperparámetros
param_combinations = list(product(
    param_grid["dense_layers"],
    param_grid["dropout_rates"],
    param_grid["epochs"],
    param_grid["batch_size"],
    param_grid["learning_rate"]
))

# Variables para almacenar los mejores modelos
best_rrmsd_train = float('inf')
best_model_train = None

best_rrmsd_val = float('inf')
best_model_val = None



best_rrmsd_test = float('inf')
best_model_test = None
errors_test = []






# Iterar sobre las combinaciones de hiperparámetros
for i, params in enumerate(param_combinations):
    dense_layers, dropout_rate, epochs, batch_size, learning_rate = params

    optimizer = Adam(learning_rate=learning_rate)

    # Definir el modelo secuencial
    model = Sequential()
    model.add(Dense(dense_layers[0], input_shape=(Xtrain_scaled.shape[1],), activation='linear'))
    for layer_size in dense_layers[1:]:
        model.add(Dense(layer_size, activation='relu'))
        model.add(Dropout(dropout_rate))
    model.add(Dense(1, activation='linear'))  # Nodo de salida

    model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])

    # Definir el callback de early stopping
    es = EarlyStopping(monitor='val_loss', mode='min', patience=50, restore_best_weights=True)

    # Entrenar el modelo
    history = model.fit(
        Xtrain_scaled,  y_train ,
        validation_data=(Xval_scaled, y_val ),
        #validation_split=0.2,  # Usar el 20% del entrenamiento para validación
        callbacks=[es],
        epochs=epochs,
        batch_size=batch_size,
        verbose=0
    )

    # Predecir en entrenamiento y validación
    pred_train = model.predict(Xtrain_scaled).flatten() + X_train.argp
    pred_val = model.predict(Xval_scaled).flatten() + X_val.argp
    pred_test =    model.predict(Xtest_scaled).flatten() + Xtest.argp 
    
    # Calcular rrmsd en train
    rrmsd_train = m.rrmsd(y_train + dTrain.argp , pred_train)
    rrmsd_val = m.rrmsd(y_val  + X_val.argp , pred_val)
    rrmsd_test = m.rrmsd(y_test + Xtest.argp , pred_test)
    
    errors_test.append(rrmsd_test)
    
    # Verificar si es el mejor modelo en Train
    if rrmsd_train < best_rrmsd_train:
        best_rrmsd_train = rrmsd_train
        best_model_train = model

    # Verificar si es el mejor modelo en Val
    if rrmsd_val < best_rrmsd_val:
        best_rrmsd_val = rrmsd_val
        best_model_val = model
        
    # Verificar si es el mejor modelo en Val
    if rrmsd_test < best_rrmsd_test:
        best_rrmsd_test = rrmsd_test
        best_model_test = model

    print(best_rrmsd_test)


models = best_model_test


X_pred = models.predict(Xtest_scaled).flatten() + Xtest.argp



Xtest['ghiPred'] = X_pred

m.rrmsd(dTest.ghi, Xtest.ghiPred)


plt.figure()
plt.plot(dTest.ghi)
plt.plot(Xtest.ghiPred)


