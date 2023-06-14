
import numpy as np

import webbrowser
import requests

import datetime


import folium
from geopy.geocoders import Nominatim
from folium.plugins import HeatMap, MiniMap, MousePosition

import base64

from models import DatoPersona,DatoSensor,TipoMedidaEnum,SensorAUT, User
import db

from PIL import Image
def mapear(long,latt,valor,texto,imagen_path,capa):

    

        if valor > 8:
            color = 'green'
        elif valor > 4:
            color = 'orange'
        else:
            color = 'red'
        

        if valor == -1: # Para marcar los sensores
            color = 'gray'

        #Depende si la imagen esta en local o es una url
        try: 
            imagen_respuesta = requests.get(imagen_path)
            imagen_base64 = base64.b64encode(imagen_respuesta.content).decode()
           
        except:
            imagen = open('static/' + imagen_path, 'rb')
            imagen_bytes = imagen.read()
            imagen_base64 = base64.b64encode(imagen_bytes).decode()


        popup_html = f'<div style="text-align:center;"><p>{texto}</p><img src="data:image/jpeg;base64,{imagen_base64}" style="max-width: 200px; max-height: 200px;">'
        popup = folium.Popup(popup_html, max_width=300)

        marcador = folium.Marker(location=[long, latt], popup=popup, icon=folium.Icon(color=color))

        marcador.add_to(capa)


from Score import calcular_puntuacion_entrada
def MakeMap():
    print(TipoMedidaEnum)
    print("Creando Mapa...")

    geolocator = Nominatim(user_agent="Photovolta")
    location = geolocator.geocode("Madrid, Spain", timeout=5)
    madrid_coords = [location.latitude, location.longitude]
    madrid_map = folium.Map(location=madrid_coords, zoom_start=6)
    capa_Imagenes_sensores = folium.FeatureGroup(name='Sensores - Imagenes',show=False)
    capa_Epicollect = folium.FeatureGroup(name='Usuarios - Imagenes',show=False)


    # Crear una lista vacía para almacenar los datos de latitud y longitud

    #db.session.commit()

    
    # Iterar sobre las entradas de cada usuario y extraer los valores de latitud y longitud
    lista_lat_lon = []
    for entrada in db.session.query(DatoPersona).all():

        #para poder poner en timestamp 
        cadena_str = entrada.fecha + " " + entrada.hora
        cadena = datetime.datetime.strptime(cadena_str, '%Y-%m-%d %H:%M')
       
        mapear(entrada.latitud,entrada.longitud,calcular_puntuacion_entrada(entrada,DatoPersona	),cadena_str,entrada.url,capa_Epicollect)
        #print(entrada.latitud)
        lista_lat_lon.append((entrada.latitud, entrada.longitud)) # Añadir los valores a la lista como una tupla

    DatosSensores = []    
    for entrada in db.session.query(DatoSensor).all():
        #mapear(entrada.latitud,entrada.longitud,entrada.analisis,entrada.hora,entrada.url,capa_marcadores)
        if entrada.tipo_medida == TipoMedidaEnum("fotografia"):
            print("estas mapeando una imagen")
            
            mapear(entrada.latitud, entrada.longitud,-1,entrada.timestamp,entrada.valor,capa_Imagenes_sensores)
        DatosSensores.append((entrada.latitud, entrada.longitud)) # Añadir los valores a la lista como una tupl
  



    Mapa_Epicollect = HeatMap(data=lista_lat_lon,name = 'Usuarios', radius=10)
    Mapa_Epicollect.add_to(madrid_map)

    MapaImagen = HeatMap(data=DatosSensores,name = 'Sensores', radius=10)
    MapaImagen.add_to(madrid_map)
    capa_Imagenes_sensores.add_to(madrid_map)
    capa_Epicollect.add_to(madrid_map)
    mouse_position = MousePosition()
    mouse_position.add_to(madrid_map)
    folium.LayerControl().add_to(madrid_map)
    MiniMap(position="bottomleft").add_to(madrid_map)
    madrid_map.save('templates/madrid_map.html')
    #madrid_map.save('madrid_map11.html')


#MakeMap()

import os
def MakeUserMap(usuario):
    print(TipoMedidaEnum)
    print("Creando Mapa...")
    if os.path.exists('templates/usermap.html'):
        os.remove('templates/usermap.html')
    
    geolocator = Nominatim(user_agent="Photovolta")
    location = geolocator.geocode("Madrid, Spain")
    madrid_coords = [location.latitude, location.longitude]
    madrid_map = folium.Map(location=madrid_coords, zoom_start=5)
    capa_Imagenes_sensores = folium.FeatureGroup(name='Imagenes',show=False)

   
    DatosSensores = []    
    for entrada in db.session.query(SensorAUT).filter_by(username_asociado=usuario).all():
        for sensor in db.session.query(DatoSensor).filter_by(id_sensor=entrada.id_sensor).all():
       
            if sensor.tipo_medida == TipoMedidaEnum("fotografia"):
           
                
                mapear(sensor.latitud, sensor.longitud,-1,sensor.timestamp,sensor.valor,capa_Imagenes_sensores)
            DatosSensores.append((sensor.latitud, sensor.longitud)) 

    mail = db.session.query(User).filter_by(username = usuario).one().email

    for entrada in db.session.query(DatoPersona).filter_by(username=mail).all():
        
        DatosSensores.append((entrada.latitud, entrada.longitud)) 
        mapear(entrada.latitud,entrada.longitud,calcular_puntuacion_entrada(entrada,DatoPersona),entrada.hora,entrada.url,capa_Imagenes_sensores)
    print(db.session.query(DatoPersona).filter_by(username=usuario).all())
  
    MapaImagen = HeatMap(data=DatosSensores,name = 'Mapa de Calor', radius=10)
    MapaImagen.add_to(madrid_map)
    capa_Imagenes_sensores.add_to(madrid_map)
    mouse_position = MousePosition()
    mouse_position.add_to(madrid_map)
    folium.LayerControl().add_to(madrid_map)
    filename = f'usermap_{usuario}.html'
    madrid_map.save(f'templates/{filename}')
