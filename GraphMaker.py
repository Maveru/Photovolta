import matplotlib.pyplot as plt
import pandas as pd
from models import DatoEpicollect,DatoValor
import db
import matplotlib.dates as mdates
import datetime
import mpld3

# Crear un DataFrame con los datos
# Crear un DataFrame con los datos

def GraphMaker():
    hora = []
    fecha = []
    irradiancia = []
    for entrada in db.session.query(DatoValor).all():
        hora.append((entrada.hora)) 
        fecha.append((entrada.fecha))
        irradiancia.append((entrada.valor_medida)) 

    df = pd.DataFrame({
        'hora': hora,
        'fecha': fecha,
        'irradiancia': irradiancia
    })

    df['hora'] = pd.to_datetime(df['hora'])

    # Creamos una nueva columna con el número del mes
    df['hora'] = df['hora'].dt.hour

    # Ordenamos los datos por la columna 'mes'
    df = df.sort_values('hora')

    # Calculamos los valores medios de irradiancia por hora
    mean_irradiancia = df.groupby('hora')['irradiancia'].mean()

    # Graficamos los valores medios de irradiancia por mes
    fig, ax = plt.subplots()
    ax.plot(mean_irradiancia.index, mean_irradiancia.values,marker='o')
    ax.set_xlabel('Hora')
    ax.set_ylabel('Irradiancia media (W/m²)')
    ax.set_xticks(range(0, 24))
    #plt.show()
    # Guardamos la gráfica en formato PNG
    fig.savefig('static/graficas/irradiancia_hora.png')



    # Convertimos la columna 'fecha' a tipo datetime
    df['fecha'] = pd.to_datetime(df['fecha'])

    # Creamos una nueva columna con el número del mes
    df['mes'] = df['fecha'].dt.month

    # Ordenamos los datos por la columna 'mes'
    df = df.sort_values('mes')

    # Calculamos los valores medios de irradiancia por mes
    mean_irradiancia = df.groupby('mes')['irradiancia'].mean()

    # Graficamos los valores medios de irradiancia por mes
    fig, ax = plt.subplots()
    ax.plot(mean_irradiancia.index, mean_irradiancia.values,marker='o')
    ax.set_xlabel('Mes')
    ax.set_ylabel('Irradiancia media (W/m²)')
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'])
    #plt.show()
    # Guardamos la gráfica en formato PNG
    fig.savefig('static/graficas/irradiancia_mes.png')


    #Mes_html = mpld3.fig(fig)
    #with open("templates\irradiancia_mes.html", "w") as f:
        #f.write(Mes_html)
    #ax.savefig('irradiancia_mes.png')

#GraphMaker()