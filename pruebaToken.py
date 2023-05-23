import cv2
import numpy as np

def calcular_svf(imagen):
    # Cargar la imagen utilizando OpenCV
    img = cv2.imread(imagen)

    # Convertir la imagen a escala de grises
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Aplicar umbralización para detectar el cielo
    _, img_threshold = cv2.threshold(img_gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Calcular el porcentaje de píxeles blancos (cielo) en relación al total
    total_pixeles = img_threshold.shape[0] * img_threshold.shape[1]
    pixeles_blancos = cv2.countNonZero(img_threshold)
    porcentaje_svf = (pixeles_blancos / total_pixeles) 

    return porcentaje_svf

# Ejemplo de uso
imagen_usuario = "image.jpg"

# Calcular SVF
svf_imagen = calcular_svf(imagen_usuario)

print("Porcentaje de píxeles blancos (cielo):", svf_imagen)



print("Puntuación obtenida", round(10*svf_imagen,2))