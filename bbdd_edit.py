import db
from models import DatoPersona, DatoSensor,User


#976
def EliminarDato(Bbdd, atributo, valor):
    datos_a_borrar = db.session.query(Bbdd).filter(getattr(Bbdd, atributo).like(valor)).all()
    if datos_a_borrar:
        for dato in datos_a_borrar:
            db.session.delete(dato)
        db.session.commit()
        print("Dato(s) borrado(s) correctamente")
    else:
        print("No se encontró ningún dato que coincida con el atributo y valor especificados")

#EliminarDato(DatoSensor,'id_sensor',5526)
#EliminarDato(DatoValor, 'id_sensor', 4310)

#EliminarDato(DatoImagen, 'id_sensor', 2610)

#EliminarDato(DatoEpicollect, 'username', 'asd@mail.com')

def LimpiarBase(Bbdd):
    datos_a_borrar = db.session.query(Bbdd).all()
    for dato in datos_a_borrar:
        db.session.delete(dato)
        db.session.commit()
    print("Base de datos limpia")    


#LimpiarBase(DatoPersona)

