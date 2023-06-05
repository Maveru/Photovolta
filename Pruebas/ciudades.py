from geopy.geocoders import Nominatim

def obtener_ciudad(latitud, longitud):
    geolocator = Nominatim(user_agent="mi_aplicacion")
    location = geolocator.reverse((latitud, longitud), exactly_one=None)
    if location:
        return location['address'].get('country', '')
    else:
        return "Ciudad no encontrada"

# Ejemplo de uso
latitud = 40.7128
longitud = -74.0060
ciudad = obtener_ciudad(latitud, longitud)
print(ciudad)
