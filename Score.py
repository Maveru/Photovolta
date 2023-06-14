from math import radians, sin, cos, sqrt, atan2
import db
from models import DatoPersona,DatoSensor,SensorAUT,User

def calcular_distancia(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia en kilómetros entre dos puntos geográficos
    utilizando la fórmula de Haversine.
    """
    # Radio aproximado de la Tierra en kilómetros
    radio_tierra = 6371.0

    # Convertir latitud y longitud a radianes
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    # Diferencia de latitud y longitud
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Aplicar la fórmula de Haversine
    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Distancia entre los dos puntos
    distancia = radio_tierra * c
    return distancia



# Ejemplo de uso


def AsignarPuntos(usuario):

    """
    Calcula la puntuación total de un usuario, sumando la puntuacion de entradas manuales
    y de entradas de sensores con un ponderacion
    """
    puntos = []
    puntuaciones = 0
    puntosMan = 0

    for entrada in db.session.query(DatoPersona).filter_by(username=usuario.email).all():
       puntosMan = puntosMan+entrada.analisis

    puntosSensores = 0
    for entrada in db.session.query(SensorAUT).filter_by(username_asociado=usuario.username).all():
        puntosSensores = puntosSensores + db.session.query(DatoSensor).filter_by(id_sensor=entrada.id_sensor).count()

    print(puntosMan*0.75 + puntosSensores*0.25)
    return puntosMan*0.75 + puntosSensores*0.25
    


def calcular_puntuacion_entrada(entrada, database):
    """
    Calcula la puntuación para una entrada específica en función de las distancias
    con todas las demás entradas.
    """
    puntuacion_punto = 0
    counter = -1
    lat1 = entrada.latitud
    lon1 = entrada.longitud

    puntos = db.session.query(database).all()
    for punto in puntos:
        if punto == entrada:
            continue #salta a la siguiente iteración 

        lat2 = punto.latitud
        lon2 = punto.longitud
        distancia = calcular_distancia(lat1, lon1, lat2, lon2)
        #print(distancia)
        if distancia <= 1.5:
            counter += 1

    if counter < 0:
        puntuacion_punto = 10
    elif counter <= 1:
        puntuacion_punto = 5
    elif counter <= 3:
        puntuacion_punto = 3
    else:
        puntuacion_punto = 1

    return puntuacion_punto


