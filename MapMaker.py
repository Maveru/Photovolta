

#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg

import urllib.request

import numpy as np

import webbrowser
import requests

import cv2

import datetime


import folium
from geopy.geocoders import Nominatim
from folium.plugins import HeatMap, MiniMap, MousePosition

import base64

from models import DatoEpicollect,DatoImagen,DatoValor
import db
import sys

from PIL import Image
def mapear(long,latt,mensaje,texto,imagen_path,capa):

       
        if mensaje > 8:
            color = 'green'
        elif mensaje > 5:
            color = 'orange'
        else:
            color = 'red'
        
        #Depende si la imagen esta en local o es una url
        try: 
            imagen = open(imagen_path, 'rb')
            imagen_bytes = imagen.read()
            imagen_base64 = base64.b64encode(imagen_bytes).decode()
        except:
            imagen_respuesta = requests.get(imagen_path)
            imagen_base64 = base64.b64encode(imagen_respuesta.content).decode()


        popup_html = f'<div style="text-align:center;"><p>{texto}</p><img src="data:image/jpeg;base64,{imagen_base64}" style="max-width: 200px; max-height: 200px;">'
        popup = folium.Popup(popup_html, max_width=300)

        marcador = folium.Marker(location=[long, latt], popup=popup, icon=folium.Icon(color=color))

        marcador.add_to(capa)



def analyze_image(url):
        # Descarga la imagen desde la URL
        with urllib.request.urlopen(url) as url_response:
            s = url_response.read()
        arr = np.asarray(bytearray(s), dtype=np.uint8)
        # Convierte la imagen en una matrix
        img = cv2.imdecode(arr, -1)
        
        # Convierte la imagen a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Crea un detector de bordes Canny
        edges = cv2.Canny(gray, 100, 200)
        
        # Aplica una transformación de Hough para detectar líneas
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
        
        # Si se detectan líneas, es una imagen de suelo
        if lines is not None:
            # Calcula la puntuación en función de la uniformidad de la iluminación
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            laplacian = cv2.Laplacian(blur, cv2.CV_64F)
            variance = np.var(laplacian)
            score = max(0, min(10, (variance - 20) / 10 + 5))
            return round(score, 2)
        
        # Si no se detectan líneas, no es una imagen de suelo
        else:
            return 0




def MakeMap():
    
    print("Creando Mapa...")

    geolocator = Nominatim(user_agent="Photovolta")
    location = geolocator.geocode("Madrid, Spain")
    madrid_coords = [location.latitude, location.longitude]
    madrid_map = folium.Map(location=madrid_coords, zoom_start=6)
    capa_marcadores = folium.FeatureGroup(name='Imagenes',show=False)
    capa_Epicollect = folium.FeatureGroup(name='Epicollect - Imagenes',show=False)


    # Crear una lista vacía para almacenar los datos de latitud y longitud

    #db.session.commit()

    
    # Iterar sobre las entradas de cada usuario y extraer los valores de latitud y longitud
    lista_lat_lon = []
    for entrada in db.session.query(DatoEpicollect).all():

        #para poder poner en timestamp 
        cadena_str = entrada.fecha + " " + entrada.hora
        cadena = datetime.datetime.strptime(cadena_str, '%Y-%m-%d %H:%M')
       
        mapear(entrada.latitud,entrada.longitud,entrada.analisis,cadena_str,entrada.url,capa_Epicollect)
        #print(entrada.latitud)
        lista_lat_lon.append((entrada.latitud, entrada.longitud)) # Añadir los valores a la lista como una tupla



    DatosValores = []
    for entrada in db.session.query(DatoValor).all():
        #mapear(entrada.latitud,entrada.longitud,entrada.analisis,entrada.hora,entrada.url,capa_marcadores)
        DatosValores.append((entrada.latitud, entrada.longitud)) # Añadir los valores a la lista como una tupla

    DatosImagen = []    
    for entrada in db.session.query(DatoImagen).all():
        #mapear(entrada.latitud,entrada.longitud,entrada.analisis,entrada.hora,entrada.url,capa_marcadores)
        mapear(entrada.latitud, entrada.longitud,10,entrada.hora,entrada.imagen,capa_marcadores)
        DatosImagen.append((entrada.latitud, entrada.longitud)) # Añadir los valores a la lista como una tupl


    #input('Presione cualquier tecla para salir...')


    Mapa_Epciollect = HeatMap(data=lista_lat_lon,name = 'Epicollect', radius=10)
    Mapa_Epciollect.add_to(madrid_map)
   # Mapa_CSV = HeatMap(data=lista_lat_lon,name = 'Sensores', radius=10)
   # Mapa_CSV.add_to(madrid_map)
    MapaImagen = HeatMap(data=DatosImagen,name = 'Camaras', radius=10)
    MapaImagen.add_to(madrid_map)
    MapaValors = HeatMap(data=DatosValores,name = 'Sensores detectores', radius=10)
    MapaValors.add_to(madrid_map)
    capa_marcadores.add_to(madrid_map)
    capa_Epicollect.add_to(madrid_map)
    mouse_position = MousePosition()
    mouse_position.add_to(madrid_map)
    folium.LayerControl().add_to(madrid_map)
    MiniMap(position="bottomleft").add_to(madrid_map)
    #madrid_map.save('templates/madrid_map.html')
    madrid_map.save('templates/madrid_map.html')
