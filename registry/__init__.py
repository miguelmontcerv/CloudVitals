import logging
import azure.functions as func
import mysql.connector
import json
from datetime import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Conexión a la base de datos
    cnx = mysql.connector.connect(user="miguel", password="***************", host="*************.mysql.database.azure.com", port=3306, database="cloudvitals", ssl_disabled=False)
    cursor = cnx.cursor()
            
    if req.method == 'POST':
        id_zona = req.params.get('id_zona')
        if id_zona:
            try:
                # Consultar el registro en la tabla 'zonas'
                query = "SELECT * FROM zonas WHERE id_zona = %s"
                value = (id_zona,)
                cursor.execute(query, value)

                # Verificar si el registro existe
                if cursor.fetchone():
                    # El registro existe
                    try:
                        datos = req.get_json()

                        campos_requeridos = ['cuenta_zona', 'mediciones', 'variable']
                        for campo in campos_requeridos:
                            if campo not in datos:
                                return func.HttpResponse('Error: El campo {} es requerido.'.format(campo), status_code=400)

                        # Insertar los datos en la tabla 'registros'
                        query = "INSERT INTO registros (cuenta_zona, id_zona, fecha, mediciones, variable) VALUES (%s, %s, %s, %s, %s)"
                        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                        values = (datos['cuenta_zona'], id_zona, fecha_actual, datos['mediciones'], datos['variable'])
                        cursor.execute(query,values)
                        cnx.commit()

                    except Exception as e:
                        cnx.rollback()
                        return func.HttpResponse('Error al realizar el insert en registros: {}'.format(str(e)), status_code=500)
                    
                    return func.HttpResponse(f"Registro con id_zona '{id_zona}' encontrado en la base de datos. Los datos han sido colocados en 'registros'!", status_code=200)
                else:
                    # El registro no existe, retornar un Bad Request
                    return func.HttpResponse(f"No se encontró el registro con id_zona '{id_zona}' en la base de datos.", status_code=400)

            except Exception as e:
                return func.HttpResponse('Error al realizar la consulta: {}'.format(str(e)), status_code=500)
            
            finally:
                cursor.close()
                cnx.close()

        else:
            return func.HttpResponse("Debe proporcionar el parámetro 'id_zona' en la cadena de consulta.", status_code=400)
    
    elif req.method == 'GET':
        id_zona = req.params.get('id_zona')
        num = req.params.get('num')
        variable = req.params.get('variable')

        try:
            # Consultar el registro en la tabla 'zonas'
            num = int(num)
            query = "SELECT mediciones FROM registros WHERE id_zona = %s AND variable = %s ORDER BY cuenta_zona DESC LIMIT %s"
            value = (id_zona, variable, num)
            cursor.execute(query, value)

            # Obtener los resultados
            resultados = cursor.fetchall()

            # Crear una lista para almacenar los valores de 'mediciones'
            mediciones_list = []
            for resultado in resultados:
                mediciones_list.extend(json.loads(resultado[0]))  # El resultado es una tupla, el primer elemento es el valor de 'mediciones'


            # Devolver los resultados en la respuesta
            return func.HttpResponse(json.dumps(mediciones_list), mimetype="application/json")
        
        except Exception as e:
                return func.HttpResponse('Error al realizar la consulta de las mediciones: {}'.format(str(e)), status_code=500)
            
        finally:
            cursor.close()
            cnx.close()