#Codigo que permite descargar datos de epicollect
import pyepicollect as pyep
import urllib.request
import numpy as np
import cv2
import pprint
from models import DatoPersona

import db
import datetime
#se puede borrar



def detectar_cielo(imagenURL):
    # Convertir la imagen a escala de grises


    
    if imagenURL.startswith('http'):
        with urllib.request.urlopen(imagenURL) as url_response:
            s = url_response.read()
        arr = np.asarray(bytearray(s), dtype=np.uint8)
        img = cv2.imdecode(arr, -1)
    else:
        img = cv2.imread(imagenURL, cv2.IMREAD_UNCHANGED)


    imagen_gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Aplicar un umbral para obtener una imagen binaria
    umbral = 200  # Ajusta este valor según sea necesario
    _, imagen_binaria = cv2.threshold(imagen_gris, umbral, 255, cv2.THRESH_BINARY)

    # Encontrar contornos en la imagen binaria
    contornos, _ = cv2.findContours(imagen_binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filtrar los contornos por área para eliminar posibles falsos positivos
    area_minima = 1000  # Ajusta este valor según sea necesario
    contornos_filtrados = [cnt for cnt in contornos if cv2.contourArea(cnt) > area_minima]

    # Devolver los contornos filtrados
    return contornos_filtrados


def analyze_image(imagenURL):
    # Convertir la imagen al espacio de color HSV
    
    
    if len(detectar_cielo(imagenURL)) < 2:
        return 0
    else:

        if imagenURL.startswith('http'):
            with urllib.request.urlopen(imagenURL) as url_response:
                s = url_response.read()
            arr = np.asarray(bytearray(s), dtype=np.uint8)
            img = cv2.imdecode(arr, -1)
        else:
            img = cv2.imread(imagenURL, cv2.IMREAD_UNCHANGED)


        imagen_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Definir el rango de azul en el espacio de color HSV
        rango_azul_bajo = np.array([90, 50, 50])
        rango_azul_alto = np.array([130, 255, 255])

        # Aplicar una máscara para obtener solo los píxeles azules del cielo
        mascara = cv2.inRange(imagen_hsv, rango_azul_bajo, rango_azul_alto)

        # Contar el número de píxeles azules en la máscara
        cantidad_pixeles_azules = np.sum(mascara == 255)

        # Calcular el porcentaje de píxeles azules respecto al total
        if img is not None:
            total_pixeles = img.shape[0] * img.shape[1]
        else:
            total_pixeles = 0
        porcentaje_azul = (cantidad_pixeles_azules / total_pixeles) * 100

        # Devolver el porcentaje de píxeles azules
        return round(0.1*porcentaje_azul,2)


def Epicollect_GetData():

    #db.Base.metadata.create_all(db.engine)
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

    #pp.pprint(entries['data']) #para verlos biem

    data = entries['data']


  
    flag = 1

    Database =  db.session.query(DatoPersona).all()

  
    print("holabucle")
    # Iterar sobre las entradas e imprimir la fecha y hora de cada una
    for entry in data['entries']:

        if flag == 0:
            print("La bbdd ya esta actualizada")
            break

        user = entry['user'].lower()
        latitud = entry['lugar']['latitude']
        longitud = entry['lugar']['longitude']
        fecha = entry['fecha']
        hora = entry['hora']
        url = entry['fotografia']
    
        #Diccionario que guarda cada entrada de Epicollect
        #entrada = {"Usuario":user,"Latitud":latitud,"Longitud":longitud,"Fecha":fecha,"Hora":hora,"Analisis":analyze_image(url),"url":url} 

        origen = "Epicollect5"
        Dato = DatoPersona(origen,user,latitud,longitud,fecha.replace("/","-"),hora,analyze_image(url),url)
        
    
        Database = db.session.query(DatoPersona).filter_by(url=url).first()
        
        if Database is None:
            db.session.add(Dato)
            db.session.commit()
            print("Dato insertado")
        else: flag = 0
        

       


#Epicollect_GetData()
#mapear()

