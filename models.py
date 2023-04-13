import db

from sqlalchemy import Column, Integer, String, Float

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
    


class DatoTabla(db.Base):
    __tablename__ = 'datostabla'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), nullable=False)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    fecha = Column(String(20), nullable=False)
    hora = Column(String(20), nullable=False)
    analisis = Column(Float, nullable=False)
    url = Column(String(200), nullable=False)

    def __init__(self, username, latitud,longitud,fecha,hora,analisis,url):
        self.username = username
        self.latitud = latitud
        self.longitud = longitud
        self.fecha = fecha
        self.hora = hora
        self.analisis = analisis
        self.url = url

    def __repr__(self):
        return f"<Dato {self.id}>"
    