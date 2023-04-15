
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

#se puede borrar
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


def mapear(long,latt,mensaje,texto,url,capa):

        """if "Hay Buena iluminacion" in mensaje:
            color = 'green'
        else:  
            color = 'red'"""
        if mensaje > 8:
            color = 'green'
        elif mensaje > 5:
            color = 'orange'
        else:
            color = 'red'
        

        imagen_respuesta = requests.get(url)
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


def Epicollect_GetData():

    db.Base.metadata.create_all(db.engine)
    pp = pprint.PrettyPrinter(indent=2)

   
        

    #Para poder sacar los datos de Epicollect
    TEST_CLIENT_ID = 3747
    TEST_CLIENT_SECRET = 'DcbIaweEE8ajduqiTjLcR30mIobz2kfOpFHoVUIr'
    TEST_NAME = 'Recoleccinn-datos-irradiancia'
    TEST_SLUG = 'recoleccinn-datos-irradiancia'


    token = pyep.auth.request_token(TEST_CLIENT_ID, TEST_CLIENT_SECRET)
    #pp.pprint(token)

    #project = pyep.api.get_project(TEST_SLUG, token['access_token'])

    entries = pyep.api.get_entries(TEST_SLUG, token['access_token'])


    pp.pprint(entries['data'])

    data = entries['data']

    #Se crea el mapa
  
    bool = 1

    Database =  db.session.query(DatoTabla).all()

    flag = 0

    print("holabucle")
    # Iterar sobre las entradas e imprimir la fecha y hora de cada una
    for entry in data['entries']:
        user = entry['user']
        latitud = entry['lugar']['latitude']
        longitud = entry['lugar']['longitude']
        fecha = entry['fecha']
        hora = entry['hora']
        url = entry['fotografia']
    
        entrada = {"Usuario":user,"Latitud":latitud,"Longitud":longitud,"Fecha":fecha,"Hora":hora,"Analisis":analyze_image(url),"url":url} #Diccionario que guarda cada entrada de Epicollect

        #Crea un diccionario para cada usuario
        Dato = DatoTabla(user,latitud,longitud,fecha,hora,analyze_image(url),url)
        
        

        for entry in Database:
            flag = flag + 1
            if entry.url == url:
                print("HAY QUE SALIR SOOOOOOOOOOOS")
                bool = 0
                break
        print(flag)
        if flag < db.session.query(DatoTabla).count():
                print("ADIOS AL SISTEMA ")
                sys.exit()
        if bool == 0:
            print("YO ME PIRO DE AQUI ")
            break
    
        #print(detect_ground(url))

        print("Sigues en el bucle")    

        #mapear(latitud,longitud,buena_iluminacion_solar(url),hora,url) # Crea un marcador para cada ubicacion con el mensaje de si hay buena iluminacion o no

        db.session.add(Dato)
        db.session.commit()

        if bool != 0:
             MakeMap()

    #print(entradas_user)
    print("------------------------------LOADING------------------------------")
    #Imprime los datos segun el usuario



def MakeMap():
    
    print("Creando Mapa...")

    geolocator = Nominatim(user_agent="Photovolta")
    location = geolocator.geocode("Madrid, Spain")
    madrid_coords = [location.latitude, location.longitude]
    madrid_map = folium.Map(location=madrid_coords, zoom_start=6)
    capa_marcadores = folium.FeatureGroup(name='Marcadores',show=False)


    # Crear una lista vacía para almacenar los datos de latitud y longitud
    lista_lat_lon = []

    #db.session.commit()


    # Iterar sobre las entradas de cada usuario y extraer los valores de latitud y longitud

    for entrada in db.session.query(DatoTabla).all():
        mapear(entrada.latitud,entrada.longitud,entrada.analisis,entrada.hora,entrada.url,capa_marcadores)
        #valor    = 10
        lista_lat_lon.append((entrada.latitud, entrada.longitud)) # Añadir los valores a la lista como una tupla
            

    #input('Presione cualquier tecla para salir...')


    mapa_calor = HeatMap(data=lista_lat_lon,name = 'Heat Map', radius=10)
    mapa_calor.add_to(madrid_map)
    capa_marcadores.add_to(madrid_map)
    mouse_position = MousePosition()
    mouse_position.add_to(madrid_map)
    folium.LayerControl().add_to(madrid_map)
    MiniMap(position="bottomleft").add_to(madrid_map)
    madrid_map.save('templates/madrid_map.html')

