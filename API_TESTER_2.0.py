import requests
import datetime
import random
from io import BytesIO
import os

import numpy as np
import cv2
url = 'http://localhost:5000/addData'

#Envio de forma manual





lat = 40.55155
lon = -3.6205

 # tamaño de la imagen
width = 500
height = 500


if 0 == 0:
    for i in range(10):


        file_name = f"archivo_{i}.png"
       
        # generando una matriz aleatoria de píxeles
        img = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)

        # guardando la imagen generada con nombre personalizado
        nombre = "random_image_{}.png".format(i)
        cv2.imwrite(nombre, img)

        with open(nombre, "rb") as file:
            imagen = file.read()
        # agregar imagen al diccionario de archivos
        files = {'imagen': (nombre, imagen)}
        
        # Generar valores aleatorios para latitude, longitude, fecha y hora
        id_sensor = random.randint(1000, 9999)
        lat_offset = random.uniform(-0.001, 0.001)
        lon_offset = random.uniform(-0.001, 0.001)
        latitude = str(lat + lat_offset)
        longitude = str(lon + lon_offset)

        
        anio_aleatorio = random.randint(2018, 2022)
        mes_aleatorio = random.randint(1, 12)
        dia_aleatorio = random.randint(1, 28)

        hour=random.randint(0, 23)


        hora_aleatoria = datetime.time(hour=random.randint(0, 23), minute=random.randint(0, 59), second=random.randint(0, 59))
        print(hora_aleatoria)

        fecha_aleatoria = datetime.date(anio_aleatorio, mes_aleatorio, dia_aleatorio)

        # Construir la entrada de datos
        entrada = {
            'id_sensor': id_sensor,
            'hora': hora_aleatoria,
            'fecha':fecha_aleatoria,
            'latitud': latitude,
            'longitud': longitude,
            
        }

        # Realizar la solicitud POST
        r = requests.post(url, data=entrada, files=files)

        print(nombre)
        os.remove(nombre)

      
        #print(r.text)
        


for i in range(500):
    # Generar valores aleatorios para latitude, longitude, fecha y hora
    id_sensor = random.randint(1000, 9999)
    lat_offset = random.uniform(-0.001, 0.001)
    lon_offset = random.uniform(-0.001, 0.001)
    latitude = str(lat + lat_offset)
    longitude = str(lon + lon_offset)
    hour=random.randint(0, 23)
    hora_aleatoria = datetime.time(hour, minute=random.randint(0, 59), second=random.randint(0, 59))
    print(hora_aleatoria)


    anio_aleatorio = random.randint(2018, 2022)
    mes_aleatorio = random.randint(1, 12)
    dia_aleatorio = random.randint(1, 28)
    fecha_aleatoria = datetime.date(anio_aleatorio, mes_aleatorio, dia_aleatorio)

    if mes_aleatorio in [3, 4, 5, 9, 10]: # Primavera y Otoño
        if 10 <= hour <= 17:
            valor_medida = 600 # Sumar 100
        elif (8 <= hour < 10) or (17 < hour <= 20):
            valor_medida = 550 # Sumar 50
        else:
            valor_medida = 0 # Sin cambios
    elif mes_aleatorio in [6, 7, 8]: # Verano
        if 10 <= hour <= 17:
            valor_medida = 800 # Sumar 100
        elif (7 <= hour < 10) or (17 < hour <= 21):
            valor_medida = 700 # Sumar 50
        else:
            valor_medida = 0 # Sin cambios
    else: # Invierno
        if 10 <= hour <= 17:
            valor_medida = 500 # Sumar 100
        elif (7 <= hour < 10) or (17 < hour <= 21):
            valor_medida = 400 # Sumar 50
        else:
            valor_medida = 0 # Sin cambioss

    valor_medida = valor_medida + random.randint(0, 150) + random.randint(0,10)*0.1
    # Construir la entrada de datos


    entrada = {
        'id_sensor': id_sensor,
        'fecha': fecha_aleatoria,
        'hora':hora_aleatoria,
        'latitud': latitude,
        'longitud': longitude,
        'valor_medida':valor_medida,
    }

    # Realizar la solicitud POST
    r = requests.post(url, data=entrada)
    print(r.text)



