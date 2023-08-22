import azure.functions as func
import json
import mysql.connector
import hashlib
import json

def generarHash(datos):
    # Convertir los datos en formato JSON a un string
    datos_str = json.dumps(datos, sort_keys=True)

    # Generar el hash utilizando SHA-256
    hash_obj = hashlib.sha256(datos_str.encode())
    id_zona = hash_obj.hexdigest()

    return id_zona

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Obtener los datos del cuerpo de la solicitud HTTP en formato JSON
        datos = req.get_json()

        # Validar que todos los campos requeridos estén presentes en el JSON
        campos_requeridos = ['tipoCultivo', 'tipoPlanta', 'tipoFruto', 'quimicos_abono',
                             'quimicos_fertilizante', 'extensionTerritorial', 'zonaCultivo',
                             'humedadTierra', 'temperaturaPromedio', 'precipitacionZona']

        for campo in campos_requeridos:
            if campo not in datos:
                return func.HttpResponse('Error: El campo {} es requerido.'.format(campo), status_code=400)

        # Conexión a la base de datos
        cnx = mysql.connector.connect(user="miguel", password="Ubuntupassword1", host="cloudvitalsdb.mysql.database.azure.com", port=3306, database="cloudvitals", ssl_disabled=False)
        cursor = cnx.cursor()

        id_zona = generarHash(datos)

        try:
            # Insertar los datos en la tabla 'zonas'
            query = "INSERT INTO zonas (id_zona, tipoCultivo, tipoPlanta, tipoFruto, quimicos_abono, quimicos_fertilizante, extensionTerritorial, zonaCultivo, humedadTierra, temperaturaPromedio, precipitacionZona) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = (id_zona, datos['tipoCultivo'], datos['tipoPlanta'], datos['tipoFruto'],
                        datos['quimicos_abono'], datos['quimicos_fertilizante'], datos['extensionTerritorial'],
                        datos['zonaCultivo'], datos['humedadTierra'], datos['temperaturaPromedio'],
                        datos['precipitacionZona'])
            cursor.execute(query,values)
            cnx.commit()

        except Exception as e:
            cnx.rollback()
            return func.HttpResponse('Error al realizar el insert: {}'.format(str(e)), status_code=500)
        
        finally:
            cursor.close()
            cnx.close()

        zona_return = {'id_zona': id_zona}
        # Convertir el diccionario a un JSON válido
        json_response = json.dumps(zona_return)
        # Enviar la respuesta HTTP con el JSON
        return func.HttpResponse(json_response, status_code=200)

    except Exception as e:
        return func.HttpResponse('Error: {}'.format(str(e)), status_code=500)
