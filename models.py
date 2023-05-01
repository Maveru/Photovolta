import db

from sqlalchemy import Column, Integer, String, Float,ForeignKey

from datetime import datetime

class User(db.Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(15), nullable=False)
    email = Column(String(80), nullable=False)
    password = Column(String(50), nullable=False)
    score = Column(Float, nullable=False)

    def __init__(self, username, email,password):
        self.username = username
        self.email = email
        self.password = password
        self.score = 0

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
    


class DatoImagen(db.Base):
    __tablename__ = 'DatoImagen'

    id = Column(Integer, primary_key=True)
    id_sensor = Column(Integer, nullable=False)
    fecha = Column(String(20), nullable=False)
    hora= Column(String(20), nullable=False)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    imagen = Column(String(200), nullable=False)

    def __init__(self, id_sensor, latitud,longitud,fecha,hora,imagen):
        self.id_sensor = id_sensor
        self.fecha = fecha
        self.hora = hora
        self.latitud = latitud
        self.longitud = longitud
        self.imagen = imagen

    def __repr__(self):
        return f"<DatoImagen {self.id}>"


class DatoValor(db.Base):
    __tablename__ = 'DatoValor'
 
    id = Column(Integer, primary_key=True)
    id_sensor = Column(Integer, nullable=False)
    fecha = Column(String(20), nullable=False)
    hora = Column(String(20), nullable=False)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    valor_medida = Column(Float, nullable=False)

    def __init__(self, id_sensor, latitud,longitud,fecha,hora,valor_medida):
        self.id_sensor = id_sensor
        self.fecha = fecha
        self.hora = hora
        self.latitud = latitud
        self.longitud = longitud
        self.valor_medida = valor_medida

    def __repr__(self):
        return f"<DatoValor {self.id}>"
    




class DatoEpicollect(db.Base):
    __tablename__ = 'DatoEpicollect'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), nullable=False)
    fecha = Column(String(20), nullable=False)
    hora = Column(String(20), nullable=False)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    analisis = Column(Float, nullable=False)
    url = Column(String(200), nullable=False)

    def __init__(self, username, latitud,longitud,fecha,hora,analisis,url):
        self.username = username
        self.fecha = fecha
        self.hora = hora
        self.latitud = latitud
        self.longitud = longitud
        self.analisis = analisis
        self.url = url

    def __repr__(self):
        return f"<Dato {self.id}>"
    
