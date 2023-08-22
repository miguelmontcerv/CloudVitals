import logging
import azure.functions as func
import mysql.connector
import json
import requests

def convertir_tipo_cultivo(tipo_cultivo):
    tipos_cultivo = {
        "Maíz": 1,
        "Tomates": 2,
        "Trigo": 3,
        "Chile": 4,
        "Calabaza": 5,
        "Arroz": 6,
        "Papa": 7,
        "Frijol": 8,
        "Cebolla": 9,
        "Sandía": 10,
        "Zanahoria": 11,
        "Aguacate": 12
    }
    return tipos_cultivo.get(tipo_cultivo, None)

def convertir_tipo_planta(tipo_planta):
    tipos_planta = {
        "Monocotiledónea": 1,
        "Dicotiledónea": 2
    }
    return tipos_planta.get(tipo_planta, None)

def convertir_tipo_fruto(tipo_fruto):
    tipos_fruto = {
        "Grano": 1,
        "Hortaliza": 2,
        "Tubérculo": 3,
        "Legumbre": 4,
        "Bulbo": 5,
        "Fruta": 6,
        "Raíz": 7
    }
    return tipos_fruto.get(tipo_fruto, None)

def convertir_zona_cultivo(zona_cultivo):
    zonas_cultivo = {
        "Región Central": 1,
        "Región Costera": 2,
        "Región Norte": 3,
        "Región Sur": 4,
        "Región Andina": 5
    }
    return zonas_cultivo.get(zona_cultivo, None)

def main(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == 'GET':
        cnx = mysql.connector.connect(user="miguel", password="Ubuntupassword1", host="cloudvitalsdb.mysql.database.azure.com", port=3306, database="cloudvitals", ssl_disabled=False)
        cursor = cnx.cursor()

        id_zona = req.params.get('id_zona')

        if id_zona:
            try:
                # Consultar el registro en la tabla 'zonas'
                query = "SELECT tipoCultivo,tipoPlanta, tipoFruto, quimicos_abono, quimicos_fertilizante, extensionTerritorial, zonaCultivo, humedadTierra,temperaturaPromedio, precipitacionZona from zonas WHERE id_zona = %s"
                value = (id_zona,)
                cursor.execute(query, value)

                datos = cursor.fetchone()

                if datos:
                    # Convertir la tupla en un diccionario
                    keys = ['tipoCultivo', 'tipoPlanta', 'tipoFruto', 'quimicos_abono', 'quimicos_fertilizante', 'extensionTerritorial', 'zonaCultivo', 'humedadTierra', 'temperaturaPromedio', 'precipitacionZona']
                    datos_dict = dict(zip(keys, datos))

                    # Convertir datos_dict a solo números.
                    datos_dict['tipoCultivo'] = convertir_tipo_cultivo(datos_dict['tipoCultivo'])
                    datos_dict['tipoPlanta'] = convertir_tipo_planta(datos_dict['tipoPlanta'])
                    datos_dict['tipoFruto'] = convertir_tipo_fruto(datos_dict['tipoFruto'])
                    datos_dict['zonaCultivo'] = convertir_zona_cultivo(datos_dict['zonaCultivo'])
                    datos_dict['usaAbono'] = 0

                    try:
                        response = requests.post('http://20.10.44.153:8080/predict', json=datos_dict)
                        response_data = response.json()
                    except Exception as e: return func.HttpResponse('Error al realizar la consulta a la IA: {}'.format(str(e)), status_code=500)    

                    cantidadAgua = response_data.get('prediccion')

                    try: 
                        update_query = "UPDATE zonas SET cantidadAgua = %s WHERE id_zona = %s"
                        update_values = (cantidadAgua, id_zona)
                        cursor.execute(update_query, update_values)
                        cnx.commit()
                    except Exception as e:
                        return func.HttpResponse('Error al realizar la insersión de la cantidad de Agua en la base de datos: {}'.format(str(e)), status_code=500)

                    # Convertir el diccionario a JSON y devolverlo como respuesta
                    return func.HttpResponse(json.dumps(cantidadAgua), status_code=200)
                else:
                    return func.HttpResponse("No se encontraron datos para el id_zona proporcionado.", status_code=404)
            
            except Exception as e:
                return func.HttpResponse('Error al realizar la consulta: {}'.format(str(e)), status_code=500)
            
            finally:
                cursor.close()
                cnx.close()
        else:
            return func.HttpResponse("Debe proporcionar el parámetro 'id_zona' en la cadena de consulta.", status_code=400)
        
    else:
        return func.HttpResponse("Método incorrecto.", status_code=400)
