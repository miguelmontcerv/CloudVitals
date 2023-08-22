import json
import random

def generar_datos_aleatorios(data, cantidad_datos):
    datos_generados = []

    for _ in range(cantidad_datos):
        nuevo_dato = random.choice(data).copy()

        nuevo_dato['usaAbono'] = random.choice([0, 1])

        nuevo_dato['extensionTerritorial'] += random.randint(-200, 200)
        nuevo_dato['cantidadAgua'] += random.randint(-100, 100)
        nuevo_dato['humedadTierra'] += random.uniform(-0.1, 0.1)
        nuevo_dato['temperaturaPromedio'] += random.randint(-5, 5)
        nuevo_dato['precipitacionZona'] += random.randint(-100, 100)

        datos_generados.append(nuevo_dato)

    return datos_generados

# Lectura del archivo data.json
with open('data_numbers.json') as file:
    data = json.load(file)

# Generación de datos aleatorios
cantidad_datos = 10000
datos_generados = generar_datos_aleatorios(data, cantidad_datos)

# Escritura de los datos generados en datos_generados.json
with open('datos_generados.json', 'w') as file:
    json.dump(datos_generados, file, indent=4, ensure_ascii=False)

print("Datos generados exitosamente.")
