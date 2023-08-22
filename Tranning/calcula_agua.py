import json
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
import joblib

# Cargar el modelo entrenado y el encoder
loaded_model = tf.keras.models.load_model('modelo_entrenado.h5')
loaded_encoder = joblib.load('encoder.joblib')

# Leer los datos desde el archivo JSON
with open('datos_entrada.json') as file:
    data = json.load(file)

# Preprocesar el ejemplo de dato de entrada
entrada = [
    data['tipoCultivo'],
    data['tipoPlanta'],
    data['tipoFruto'],
    int(data['usaAbono']),
    int(data['quimicos']['abono']),
    int(data['quimicos']['fertilizante']),
    data['extensionTerritorial'],
    data['zonaCultivo'],
    data['humedadTierra'],
    data['temperaturaPromedio'],
    data['precipitacionZona']
]

entrada_encoded = loaded_encoder.transform(np.array(entrada)[[0, 1, 2, 7]].reshape(1, -1)).toarray()
entrada_preprocesada = np.concatenate([entrada_encoded, np.array(entrada)[[3, 4, 5, 6, 8, 9, 10]].reshape(1, -1)], axis=1)

# Realizar la predicción utilizando el modelo cargado
prediccion = loaded_model.predict(entrada_preprocesada)
print('Predicción de cantidad de agua:', prediccion[0][0])