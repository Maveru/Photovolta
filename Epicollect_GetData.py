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



def analyze_image(image_path_or_url):
    # Verifica si la entrada es una URL o una ruta local
    if image_path_or_url.startswith('http'):
        with urllib.request.urlopen(image_path_or_url) as url_response:
            s = url_response.read()
        arr = np.asarray(bytearray(s), dtype=np.uint8)
        img = cv2.imdecode(arr, -1)
    else:
        img = cv2.imread(image_path_or_url, cv2.IMREAD_UNCHANGED)
    # Convertir la imagen a escala de grises
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Aplicar umbralización para detectar el cielo
    _, img_threshold = cv2.threshold(img_gray, 180, 255, cv2.THRESH_BINARY_INV)


    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Crea un detector de bordes Canny
    edges = cv2.Canny(gray, 100, 200)
        
        # Aplica una transformación de Hough para detectar líneas
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
        
        # Si se detectan líneas, es una imagen de suelo
    score = 0
    if lines is not None:
            # Calcula la puntuación en función de la uniformidad de la iluminación
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        laplacian = cv2.Laplacian(blur, cv2.CV_64F)
        variance = np.var(laplacian)
        score = max(0, min(10, (variance - 20) / 10 + 5))
        

    # Calcular el porcentaje de píxeles blancos (cielo) en relación al total
    total_pixeles = img_threshold.shape[0] * img_threshold.shape[1]
    pixeles_blancos = cv2.countNonZero(img_threshold)
    porcentaje_svf = (pixeles_blancos / total_pixeles) 

    if score > 8:
        return 0
    
    return round(10*porcentaje_svf,2)


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

