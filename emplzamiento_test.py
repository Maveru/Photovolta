from geopy.distance import geodesic

# Definir una distancia mínima para considerar diferentes emplazamientos (en metros)
distancia_minima = 1000

# Lista para almacenar los emplazamientos
emplazamientos = []

# Función para verificar si un punto pertenece a un emplazamiento existente
def pertenece_a_emplazamiento(punto, emplazamientos):
    for emplazamiento in emplazamientos:
        distancia = geodesic(punto, emplazamiento).meters
        if distancia <= distancia_minima:
            return True
    return False

# Función para agregar un nuevo emplazamiento
def agregar_emplazamiento(punto, emplazamientos):
    emplazamientos.append(punto)

# Ejemplo de medidas tomadas (latitud, longitud)
medidas = [
    (40.7128, -74.0060),  # Nueva York
    (34.0522, -118.2437),  # Los Ángeles
    (41.8781, -87.6298),  # Chicago
    (40.250, -74.150),  # Nueva York (repetido)
    (51.5074, -0.1278)  # Londres
]

# Procesar las medidas
for medida in medidas:
    if not pertenece_a_emplazamiento(medida, emplazamientos):
        agregar_emplazamiento(medida, emplazamientos)

# Imprimir los emplazamientos
for i, emplazamiento in enumerate(emplazamientos, 1):
    print(f"Emplazamiento {i}: {emplazamiento}")
