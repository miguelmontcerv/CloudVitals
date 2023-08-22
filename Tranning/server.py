import json
import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify
from sklearn.preprocessing import OneHotEncoder
import joblib

app = Flask(__name__)

# Cargar el modelo entrenado y el encoder
try:
    loaded_model = tf.keras.models.load_model('modelo_entrenado.h5')
    loaded_encoder = joblib.load('encoder.joblib')
except Exception as e:
    print("\n\n\tNO SE PUEDEN CARGAR LOS MODELOS")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Obtener el JSON del cuerpo de la petición
        data = request.get_json()
    except Exception as e:
        return func.HttpResponse(json.dumps({"mensaje:" : "No se pudo abrir el body del request","error": str(e)}), status_code=500, mimetype='application/json')

    # Preprocesar el ejemplo de dato de entrada
    try:
        entrada = [
            data['tipoCultivo'],
            data['tipoPlanta'],
            data['tipoFruto'],
            int(data['usaAbono']),
            int(data['quimicos_abono']),
            int(data['quimicos_fertilizante']),
            data['extensionTerritorial'],
            data['zonaCultivo'],
            data['humedadTierra'],
            data['temperaturaPromedio'],
            data['precipitacionZona']
        ]

        entrada_encoded = loaded_encoder.transform(np.array(entrada)[[0, 1, 2, 7]].reshape(1, -1)).toarray()
        entrada_preprocesada = np.concatenate([entrada_encoded, np.array(entrada)[[3, 4, 5, 6, 8, 9, 10]].reshape(1, -1)], axis=1)
    
    except Exception as e:
        return func.HttpResponse(json.dumps({"mensaje:" : "No se pudieron serealizar los datos","error": str(e)}), status_code=500, mimetype='application/json')

    # Realizar la predicción utilizando el modelo cargado
    try:
        prediccion = loaded_model.predict(entrada_preprocesada)
    except Exception as e:
        return func.HttpResponse(json.dumps({"mensaje:" : "No se pudieron realizar las predicciones","error": str(e)}), status_code=500, mimetype='application/json')
    
    # Devolver la predicción como respuesta en formato JSON
    return jsonify({'prediccion': str(prediccion[0][0])})

@app.route('/entry', methods=['POST'])
def entry():
    data = request.get_json()
    print("\n\tLos datos han sido mandados...")
    return jsonify({'data': data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
