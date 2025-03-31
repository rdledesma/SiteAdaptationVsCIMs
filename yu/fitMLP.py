import tensorflow as tf
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from itertools import product
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.callbacks import EarlyStopping
from keras.optimizers import Adam
import Metrics as m
from Sites import Site
from Geo import Geo

site = Site('YU')

# Asegurar que TensorFlow usa la GPU
physical_devices = tf.config.experimental.list_physical_devices('GPU')
if physical_devices:
    try:
        tf.config.experimental.set_memory_growth(physical_devices[0], True)
        print("GPU habilitada correctamente")
    except RuntimeError as e:
        print(e)
else:
    print("No se detectó GPU, ejecutando en CPU.")

# Cargar datos
d = pd.read_csv('yu/cmi/FR.csv')
d['date'] = pd.to_datetime(d.date)
e = pd.read_csv('yu/meas/yu_10.csv')
e['date'] = pd.to_datetime(e.date)

# Reindexar y manejar valores faltantes
d = (d.set_index('date')
      .reindex(e.date)
      .rename_axis(['date'])
      .reset_index())

d['ghi'] = e.ghi
d = d.dropna()


dfGeo = Geo(d.date, site.lat, site.long, 
            gmt=0, 
            alt=site.alt, 
            beta=0).df

d['sza'] = dfGeo.SZA
d['CTZ'] = dfGeo.CTZ
d['argp'] = dfGeo.GHIargp2

# Dividir en conjuntos de entrenamiento y prueba
dTrain = d[d.date.dt.year == 2018]
dTest = d[d.date.dt.year == 2017]





X = d[['FR', 'sza', 'CTZ', 'argp']]



Xtest = dTest[['FR', 'sza', 'CTZ', 'argp']]
y_test = dTest.ghi

X_train, X_val, y_train, y_val = train_test_split(X, d.ghi, test_size=0.2, random_state=42)

# Normalización
scaler = MinMaxScaler()
Xtrain_scaled = scaler.fit_transform(X_train)
Xval_scaled = scaler.transform(X_val)
Xtest_scaled = scaler.transform(Xtest)



# Hiperparámetros a probar
param_grid = {
    "dense_layers": [(5, 10, 15), (10, 15, 25), (20, 25, 35), (30, 40), (40, 50)],
    "dropout_rates": [0, 0.1],
    "epochs": [60, 70, 80, 90],
    "batch_size": [40],
    "learning_rate": [0.1, 0.01]
}

# Generar combinaciones de hiperparámetros
param_combinations = list(product(
    param_grid["dense_layers"],
    param_grid["dropout_rates"],
    param_grid["epochs"],
    param_grid["batch_size"],
    param_grid["learning_rate"]
))

# Variables para almacenar el mejor modelo
best_rrmsd_test = float('inf')
best_model_test = None
errors_test = []

# Forzar entrenamiento en GPU
with tf.device('/GPU:0'):
    print("Ejecutando entrenamiento en GPU...")
    
    # Iterar sobre combinaciones de hiperparámetros
    for i, params in enumerate(param_combinations):
        dense_layers, dropout_rate, epochs, batch_size, learning_rate = params
        optimizer = Adam(learning_rate=learning_rate)

        # Definir el modelo
        model = Sequential()
        model.add(Dense(dense_layers[0], input_shape=(Xtrain_scaled.shape[1],), activation='linear'))
        for layer_size in dense_layers[1:]:
            model.add(Dense(layer_size, activation='relu'))
            model.add(Dropout(dropout_rate))
        model.add(Dense(1, activation='linear'))  # Capa de salida

        model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])

        # Callback para early stopping
        es = EarlyStopping(monitor='val_loss', mode='min', patience=50, restore_best_weights=True)

        # Entrenar modelo
        history = model.fit(
            Xtrain_scaled, y_train,
            validation_data=(Xval_scaled, y_val),
            callbacks=[es],
            epochs=epochs,
            batch_size=batch_size,
            verbose=0
        )

        # Predecir en conjunto de prueba
        pred_test = model.predict(Xtest_scaled).flatten()
        rrmsd_test = m.rrmsd(y_test, pred_test)
        errors_test.append(rrmsd_test)

        # Verificar si es el mejor modelo
        if rrmsd_test < best_rrmsd_test:
            best_rrmsd_test = rrmsd_test
            best_model_test = model

        print(f"Iteración {i+1}/{len(param_combinations)} - Mejor RRMSD Test: {best_rrmsd_test}")

# # Guardar el mejor modelo
best_model_test.save("yu/model_yu.keras")


