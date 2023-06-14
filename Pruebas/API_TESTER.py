import requests
import datetime
import random
from io import BytesIO
import os

import numpy as np
import cv2

from datetime import datetime

url = 'http://localhost:5000/addData'

#Envio de forma manual



id_sensor = 2001
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY4NjE3NjA1NCwianRpIjoiMWIxMjk3MjEtNTA2ZC00ZjZjLTgwOGEtYzFhYzRlYzI4ODE2IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MjAwMSwibmJmIjoxNjg2MTc2MDU0LCJleHAiOjE2ODYxNzY5NTR9.cQeq1U7ddtIwXg_GHeb9GR_UoWp16BAO8gOm21hfC6U"

lat = 30.58221
lon = -4.7709

 # tamaño de la imagen
width = 500
height = 500

for i in range (500):
    select = random.randint(0,1)
    select = 0

    if select == 0:
       # for i in range(10):


            file_name = f"archivo_{i}.png"
        
            # generando una matriz aleatoria de píxeles
            img = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)

            # guardando la imagen generada con nombre personalizado
            nombre = "random_image_{}.png".format(i)
            cv2.imwrite(nombre, img)

            with open(nombre, "rb") as file:
                imagen = file.read()
            # agregar imagen al diccionario de archivos
            files = {'valor_medida': (nombre, imagen)}
            
            # Generar valores aleatorios para latitude, longitude, fecha y hora
            #id_sensor = random.randint(1000, 9999)
            lat_offset = random.uniform(-0.001, 0.001)
            lon_offset = random.uniform(-0.001, 0.001)
            latitude = str(lat + lat_offset)
            longitude = str(lon + lon_offset)
            orientacion = random.randint(0, 360)
            inclinacion = random.randint(0, 90)
        
            hour = random.randint(0, 23)
            minute=random.randint(0, 59)
            second=random.randint(0, 59)

            anio_aleatorio = random.randint(2018, 2022)
            mes_aleatorio = random.randint(1, 12)
            dia_aleatorio = random.randint(1, 28)

            timestamp = datetime(anio_aleatorio,mes_aleatorio,dia_aleatorio,hour,minute,second).isoformat()

            # Construir la entrada de datos
            entrada = {
            'id_sensor': id_sensor,
            #'token' : token,
            'timestamp': timestamp,
            'latitud': latitude,
            'longitud': longitude,
            'orientacion': orientacion,
            'inclinacion': inclinacion,
            'tipo_medida' : "fotografia",
        }
            header = {
                 'token':token

            }
            # Realizar la solicitud POST
            r = requests.post(url, data=entrada, files=files,headers=header)

            #print(nombre)
            os.remove(nombre)

        
            print(r.text)
            

    if select == 1:
       # for i in range(1):
            # Generar valores aleatorios para latitude, longitude, fecha y hora
            #id_sensor = random.randint(1000, 9999)
            lat_offset = random.uniform(-0.001, 0.001)
            lon_offset = random.uniform(-0.001, 0.001)
            latitude = str(lat + lat_offset)
            longitude = str(lon + lon_offset)
            orientacion = random.randint(0, 360)
            inclinacion = random.randint(0, 90)
        
            hour = random.randint(0, 23)
            minute=random.randint(0, 59)
            second=random.randint(0, 59)

            anio_aleatorio = random.randint(2018, 2022)
            mes_aleatorio = random.randint(1, 12)
            dia_aleatorio = random.randint(1, 28)

            timestamp = datetime(anio_aleatorio,mes_aleatorio,dia_aleatorio,hour,minute,second).isoformat()
            
            #print(timestamp)

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
                'token' : token,
                'timestamp': timestamp,
                'latitud': latitude,
                'longitud': longitude,
                'orientacion': orientacion,
                'inclinacion': inclinacion,
                'tipo_medida' : "irradiancia",
                'valor_medida':valor_medida,
            }
            header = {
                 'token':token

            }

            # Realizar la solicitud POST
            r = requests.post(url, data=entrada,headers=header)
            print(r.text)


    if select == 2:
       # for i in range(2):
            # Generar valores aleatorios para latitude, longitude, fecha y hora
            #id_sensor = random.randint(1000, 9999)
            lat_offset = random.uniform(-0.001, 0.001)
            lon_offset = random.uniform(-0.001, 0.001)
            latitude = str(lat + lat_offset)
            longitude = str(lon + lon_offset)
            orientacion = random.randint(0, 360)
            inclinacion = random.randint(0, 90)
        
            hour = random.randint(0, 23)
            minute=random.randint(0, 59)
            second=random.randint(0, 59)

            anio_aleatorio = random.randint(2018, 2022)
            mes_aleatorio = random.randint(1, 12)
            dia_aleatorio = random.randint(1, 28)

            timestamp = datetime(anio_aleatorio,mes_aleatorio,dia_aleatorio,hour,minute,second).isoformat()

            
            valor_medida = float(round(random.randint(0,10)*0.1,2))
            # Construir la entrada de datos
            #print(valor_medida)

            entrada = {
                'id_sensor': id_sensor,
                'token' : token,
                'timestamp': timestamp,
                'latitud': latitude,
                'longitud': longitude,
                'orientacion': orientacion,
                'inclinacion': inclinacion,
                'tipo_medida' : "SVF",
                'valor_medida':valor_medida,
            }
            header = {
                 'token':token

            }

            # Realizar la solicitud POST
            r = requests.post(url, data=entrada,headers=header)
            print(r.text)
            

