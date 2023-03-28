
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


pp = pprint.PrettyPrinter(indent=2)

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


def mapear(long,latt,mensaje,texto,url):

    if "Hay Buena iluminacion" in mensaje:
        color = 'green'
    else:  
        color = 'red'

    imagen_respuesta = requests.get(url)
    imagen_base64 = base64.b64encode(imagen_respuesta.content).decode()

    popup_html = f'<div style="text-align:center;"><p>{texto}</p><img src="data:image/jpeg;base64,{imagen_base64}" style="max-width: 200px; max-height: 200px;">'
    popup = folium.Popup(popup_html, max_width=300)

    marcador = folium.Marker(location=[long, latt], popup=popup, icon=folium.Icon(color=color))

    marcador.add_to(capa_marcadores)


#Para poder sacar los datos de Epicollect
TEST_CLIENT_ID = 3747
TEST_CLIENT_SECRET = 'DcbIaweEE8ajduqiTjLcR30mIobz2kfOpFHoVUIr'
TEST_NAME = 'Recoleccinn-datos-irradiancia'
TEST_SLUG = 'recoleccinn-datos-irradiancia'


token = pyep.auth.request_token(TEST_CLIENT_ID, TEST_CLIENT_SECRET)
#pp.pprint(token)

project = pyep.api.get_project(TEST_SLUG, token['access_token'])

entries = pyep.api.get_entries(TEST_SLUG, token['access_token'])


#pp.pprint(entries['data'])

data = entries['data']

entradas_user = {}
longitudes = []
latitudes = []

#Se crea el mapa
geolocator = Nominatim(user_agent="Photovolta")
location = geolocator.geocode("Madrid, Spain")
madrid_coords = [location.latitude, location.longitude]
madrid_map = folium.Map(location=madrid_coords, zoom_start=6)
capa_marcadores = folium.FeatureGroup(name='Marcadores',show=False)



# Iterar sobre las entradas e imprimir la fecha y hora de cada una
for entry in data['entries']:
    user = entry['user']
    latitud = entry['lugar']['latitude']
    longitud = entry['lugar']['longitude']
    fecha = entry['fecha']
    hora = entry['hora']
    url = entry['fotografia']
    
    # Definir la URL de la imagen

    #webbrowser.open(url)
    # Abrir la URL y leer su contenido
    #with urllib.request.urlopen(url) as url:
      #  imagen_array = np.array(Image.open(url))
    # Mostrar la imagenp
   # Image.fromarray(imagen_array).show()    
    entrada = {"Usuario":user,"Latitud":latitud,"Longitud":longitud,"Fecha":fecha,"Hora":hora,"Analisis":buena_iluminacion_solar(url)} #Diccionario que guarda cada entrada de Epicollect
    
    mapear(latitud,longitud,buena_iluminacion_solar(url),hora,url) # Crea un marcador para cada ubicacion con el mensaje de si hay buena iluminacion o no
#Crea un diccionario para cada usuario
    if user in entradas_user:
        entradas_user[user].append(entrada)
    else:
        entradas_user[user] = [entrada]

#Imprime los datos segun el usuario
for user in sorted(entradas_user.keys()):
    #print("Entradas para el usuario", user,":")
    for entrada in entradas_user[user]:
        entradas_sin_user = dict(list(entrada.items())[1:]) #Quita la entrada "user"
        #print(entradas_sin_user)
        #print(entrada)
        #print(" ".join("{}: {}".format(k, v) for k, v in entradas_sin_user.items())) #Para imprimir sin {} ni ,



# Crear una lista vacía para almacenar los datos de latitud y longitud
lista_lat_lon = []

# Iterar sobre las entradas de cada usuario y extraer los valores de latitud y longitud
for usuario, entradas in entradas_user.items():
    for entrada in entradas:
        latitud  = entrada["Latitud"]
        longitud = entrada["Longitud"]
        valor    = 10
        
        lista_lat_lon.append((latitud, longitud)) # Añadir los valores a la lista como una tupla

#input('Presione cualquier tecla para salir...')
datos = []

mapa_calor = HeatMap(data=lista_lat_lon,name = 'Heat Map', radius=10)
mapa_calor.add_to(madrid_map)
capa_marcadores.add_to(madrid_map)
mouse_position = MousePosition()
mouse_position.add_to(madrid_map)
folium.LayerControl().add_to(madrid_map)
MiniMap(position="bottomleft").add_to(madrid_map)
madrid_map.save('templates/madrid_map.html')



