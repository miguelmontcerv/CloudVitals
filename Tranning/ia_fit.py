import json
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
import joblib

# Leer los datos desde el archivo JSON
with open('datos_entrenamiento.json') as file:
    data = json.load(file)

# Separar las características de la salida esperada
X = []
y = []
for item in data:
    X.append([
        item['tipoCultivo'],
        item['tipoPlanta'],
        item['tipoFruto'],
        int(item['usaAbono']),
        int(item['quimicos']['abono']),
        int(item['quimicos']['fertilizante']),
        item['extensionTerritorial'],
        item['zonaCultivo'],
        item['humedadTierra'],
        item['temperaturaPromedio'],
        item['precipitacionZona']
    ])
    y.append(item['cantidadAgua'])

# Convertir los datos a matrices NumPy
X = np.array(X)
y = np.array(y)

# Crear el encoder y codificar los datos categóricos
encoder = OneHotEncoder()
X_encoded = encoder.fit_transform(X[:, [0, 1, 2, 7]]).toarray()

# Combinar las columnas codificadas con las numéricas
X = np.concatenate([X_encoded, X[:, [3, 4, 5, 6, 8, 9, 10]]], axis=1)

# Dividir los datos en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Crear el modelo de TensorFlow
model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(32, activation='relu', input_shape=(X_train.shape[1],)),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(1)
])

# Compilar el modelo
model.compile(optimizer='adam', loss='mse')

# Entrenar el modelo
model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=1)

# Evaluar el modelo en el conjunto de prueba
loss = model.evaluate(X_test, y_test, verbose=0)
print('Loss en el conjunto de prueba:', loss)

# Guardar el modelo entrenado y el encoder en formato HDF5 (.h5)
model.save('modelo_entrenado.h5')
joblib.dump(encoder, 'encoder.joblib')

# Cargar el modelo entrenado y el encoder
loaded_model = tf.keras.models.load_model('modelo_entrenado.h5')
loaded_encoder = joblib.load('encoder.joblib')

# Crear un ejemplo de dato de entrada para hacer una predicción
ejemplo = {
    "tipoCultivo": 6,
    "tipoPlanta": 1,
    "tipoFruto": 1,
    "usaAbono": 1,
    "quimicos": {
        "abono": 1,
        "fertilizante": 0
    },
    "extensionTerritorial": 1945,
    "zonaCultivo": 4,
    "humedadTierra": 0.8720776683786328,
    "temperaturaPromedio": 35,
    "precipitacionZona": 1482
}

# Preprocesar el ejemplo de dato de entrada
entrada = [
    ejemplo['tipoCultivo'],
    ejemplo['tipoPlanta'],
    ejemplo['tipoFruto'],
    int(ejemplo['usaAbono']),
    int(ejemplo['quimicos']['abono']),
    int(ejemplo['quimicos']['fertilizante']),
    ejemplo['extensionTerritorial'],
    ejemplo['zonaCultivo'],
    ejemplo['humedadTierra'],
    ejemplo['temperaturaPromedio'],
    ejemplo['precipitacionZona']
]
entrada_encoded = loaded_encoder.transform(np.array(entrada)[[0, 1, 2, 7]].reshape(1, -1)).toarray()
entrada_preprocesada = np.concatenate([entrada_encoded, np.array(entrada)[[3, 4, 5, 6, 8, 9, 10]].reshape(1, -1)], axis=1)

# Realizar la predicción utilizando el modelo cargado
prediccion = loaded_model.predict(entrada_preprocesada)
print('Predicción de cantidad de agua:', prediccion[0][0])