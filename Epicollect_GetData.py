#Codigo que permite descargar datos de epicollect
import pyepicollect as pyep
import pprint
from models import DatoPersona
from Score import calcular_puntuacion_entrada

import db
import datetime
#se puede borrar



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
        Dato = DatoPersona(origen,user,latitud,longitud,fecha.replace("/","-"),hora,0,url)

        Dato = DatoPersona(origen,user,latitud,longitud,fecha.replace("/","-"),hora,calcular_puntuacion_entrada(Dato,DatoPersona),url)
        
    
        Database = db.session.query(DatoPersona).filter_by(url=url).first()
        
        if Database is None:
            db.session.add(Dato)
            db.session.commit()
            print("Dato insertado")
        else: flag = 0
        

       


#Epicollect_GetData()
#mapear()

