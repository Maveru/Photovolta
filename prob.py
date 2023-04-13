
import pyepicollect as pyep
#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg

import urllib.request

import numpy as np

import webbrowser
import requests

import cv2

import pprint

import folium
from geopy.geocoders import Nominatim
from folium.plugins import HeatMap, MiniMap, MousePosition

import base64

from models import DatoTabla
import db
import sys

pp = pprint.PrettyPrinter(indent=2)

#Para poder sacar los datos de Epicollect
TEST_CLIENT_ID = 3747
TEST_CLIENT_SECRET = 'DcbIaweEE8ajduqiTjLcR30mIobz2kfOpFHoVUIr'
TEST_NAME = 'Recoleccinn-datos-irradiancia'
TEST_SLUG = 'recoleccinn-datos-irradiancia'
def buena_iluminacion_solar(imagen_url, umbral=150):
    # Descargar la imagen de la URL
    imagen_arr = np.asarray(bytearray(urllib.request.urlopen(imagen_url).read()), dtype=np.uint8)
    imagen = cv2.imdecode(imagen_arr, -1)
    
    # Convertir la imagen a escala de grises
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    
    # Calcular el histograma de la imagen en escala de grises
    hist = cv2.calcHist([gris], [0], None, [256], [0, 256])
    
    # Calcular la media de los niveles de gris de la imagen
    media = np.mean(gris)
    
    # Aplicar un umbral a la imagen
    _, binaria = cv2.threshold(gris, umbral, 255, cv2.THRESH_BINARY)
    
    # Calcular el porcentaje de la imagen que está por encima del umbral
    porcentaje = (np.count_nonzero(binaria == 255) / binaria.size) * 100
    
    # Determinar si la imagen tiene buena iluminación solar
    #return porcentaje
   
    if porcentaje > 40:
        return "Hay Buena iluminacion"
    else:
        return "Iluminacion insuficiente"


token = pyep.auth.request_token(TEST_CLIENT_ID, TEST_CLIENT_SECRET)
#pp.pprint(token)

project = pyep.api.get_project(TEST_SLUG, token['access_token'])

entries = pyep.api.get_entries(TEST_SLUG, token['access_token'])


pp.pprint(entries['data'])

data = entries['data']



for entry in data['entries']:
    user = entry['user']
    latitud = entry['lugar']['latitude']
    longitud = entry['lugar']['longitude']
    fecha = entry['fecha']
    hora = entry['hora']
    url = entry['fotografia']
   
    entrada = {"Usuario":user,"Latitud":latitud,"Longitud":longitud,"Fecha":fecha,"Hora":hora,"Analisis":buena_iluminacion_solar(url),"url":url} #Diccionario que guarda cada entrada de Epicollect

#Crea un diccionario para cada usuario
    Dato = DatoTabla(user,latitud,longitud,fecha,hora,buena_iluminacion_solar(url),url)
    
    

 

    print("Sigues en el bucle")    

    #mapear(latitud,longitud,buena_iluminacion_solar(url),hora,url) # Crea un marcador para cada ubicacion con el mensaje de si hay buena iluminacion o no

    db.session.add(Dato)
    db.session.commit()

#print(entradas_user)
print("------------------------------LOADING------------------------------")
#Imprime los datos segun el usuario