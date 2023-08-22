import logging
import azure.functions as func
import mysql.connector
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == 'GET':
        cnx = mysql.connector.connect(user="miguel", password="***************", host="*************.mysql.database.azure.com", port=3306, database="cloudvitals", ssl_disabled=False)
        cursor = cnx.cursor()

        id_zona = req.params.get('id_zona')

        if id_zona:
            try:
                # Consultar el registro en la tabla 'zonas'
                query = "SELECT tipoCultivo,tipoPlanta, tipoFruto, quimicos_abono, quimicos_fertilizante, extensionTerritorial, zonaCultivo, humedadTierra,temperaturaPromedio, precipitacionZona, cantidadAgua from zonas WHERE id_zona = %s"
                value = (id_zona,)
                cursor.execute(query, value)

                datos = cursor.fetchone()

                if datos:
                    # Convertir la tupla en un diccionario
                    keys = ['tipoCultivo', 'tipoPlanta', 'tipoFruto', 'quimicos_abono', 'quimicos_fertilizante', 'extensionTerritorial', 'zonaCultivo', 'humedadTierra', 'temperaturaPromedio', 'precipitacionZona', 'cantidadAgua']
                    datos_dict = dict(zip(keys, datos))

                    # Convertir el diccionario a JSON y devolverlo como respuesta
                    return func.HttpResponse(json.dumps(datos_dict), status_code=200)
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