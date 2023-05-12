import db
import enum

from sqlalchemy import Column, Integer, String, Float,ForeignKey,Enum

from datetime import datetime



class User(db.Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(15), nullable=False)
    email = Column(String(80), nullable=False)
    password = Column(String(50), nullable=False)
    score = Column(Float, nullable=False)
    profile_picture = Column(String(200), nullable=False)

    def __init__(self, username, email,password,profile_picture):
        self.username = username
        self.email = email
        self.password = password
        self.score = 0
        self.profile_picture=profile_picture

    def __repr__(self):
        return f"<User {self.id}>"

class Comment(db.Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), nullable=False)
    comment = Column(String(500), nullable=False)
    date = Column(String(20), nullable=False)

    def __init__(self, username, comment,date):
        self.username = username
        self.comment = comment
        self.date = date

    def __repr__(self):
        return f"<Comment {self.id}>"
    


class TipoMedidaEnum(enum.Enum):
    fotografia = "fotografia"
    irradiancia = "irradiancia"
    SVF = "SVF"

class DatoSensor(db.Base):
    __tablename__ = 'DatoSensor'

    id = Column(Integer, primary_key=True)
    id_sensor = Column(Integer, nullable=False)
    timestamp = Column(String(25), nullable=False)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    orientacion = Column(Integer,nullable=False)
    tipo_medida = Column(Enum(TipoMedidaEnum),nullable=False)
  
    valor = Column(String(200), nullable=False)
    


    def __init__(self, id_sensor,timestamp, latitud,longitud,orientacion,tipo_medida,valor):
        self.id_sensor = id_sensor
        self.timestamp = timestamp
        self.latitud = latitud
        self.longitud = longitud
        self.orientacion = orientacion
        self.tipo_medida = tipo_medida
        self.valor = valor

    def __repr__(self):
        return f"<DatoSensor {self.id}>"

class DatoPersona(db.Base):
    __tablename__ = 'DatoPersona'

    id = Column(Integer, primary_key=True)
    origen = Column(String(20),nullable=False)
    username = Column(String(80), nullable=False)
    fecha = Column(String(20), nullable=False)
    hora = Column(String(20), nullable=False)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    analisis = Column(Float, nullable=False)
    url = Column(String(200), nullable=False)

    def __init__(self, origen,username, latitud,longitud,fecha,hora,analisis,url):
        self.origen = origen
        self.username = username
        self.fecha = fecha
        self.hora = hora
        self.latitud = latitud
        self.longitud = longitud
        self.analisis = analisis
        self.url = url

    def __repr__(self):
        return f"<DatoPersona {self.id}>"
    


class SensorAUT(db.Base):
    __tablename__ = 'SensorAUT'

    id = Column(Integer, primary_key=True)
    id_sensor = Column(Integer, nullable=False)
    username_asociado = Column(String(80), nullable=False)
    token = Column(String(32), nullable=False)

    def __init__(self, id_sensor, username_asociado,token):
        self.id_sensor = id_sensor
        self.username_asociado = username_asociado
        self.token = token
    
    def __repr__(self):
        return f"<Sensortoken {self.id}>"