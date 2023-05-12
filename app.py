from flask import Flask, render_template,request,redirect,url_for,session,flash,get_flashed_messages
#import folium
#import subprocess
#import os
from werkzeug.security import check_password_hash,generate_password_hash
from flask_session import Session
from datetime import datetime
from GraphMaker import GraphMaker
from MapMaker import MakeMap,analyze_image,MakeUserMap
from password_strength import PasswordPolicy
from Epicollect_GetData import Epicollect_GetData
from flask_jwt_extended import JWTManager

from PIL import Image
from flask_jwt_extended import create_access_token

#from Epicollect_GetData import DatosTabla
#from jinja2 import Environment

#from Epicollect_GetData import Epicollect_GetData,MakeMap

import db
import os
from models import Comment,User,DatoSensor,DatoPersona,SensorAUT
from bbdd_edit import EliminarDato
#from sqlalchemy import func


#flask --app .\mapflask.py run --host 0.0.0.0
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = '685b9e7b32a529df7051e23c4c490808f783e4abbc7ea933cdb502385d694ecf'  # Clave secreta para firmar los tokens JWT -- secrets.token_hex(32)
jwt = JWTManager(app)
app.secret_key = "clave_secreta"
UPLOAD_FOLDER = 'static/datosFoto/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PFP_UPLOAD_FOLDER'] = 'static/userpfp/'
Session(app)

sensores_autenticados = {}


def registrar_sensor(id_sensor):
    token = create_access_token(identity=id_sensor)
    sensores_autenticados[id_sensor] = token
    return token




@app.route('/')
def index():
    session.pop('authenticated', None)
    Nusuarios = db.session.query(User).count()#No se si pasar los registrados en la pagina o los que han mandado datos a Epicollect
   
    Ndatos = db.session.query(DatoPersona).count()

    users = db.session.query(User).all()
    score_total = 0
    
    datosPuntos = db.session.query(DatoPersona.analisis).all()
    
    for punto in datosPuntos:
            score_total += punto[0]
            print(score_total)

    


    return render_template('index.html',Nusuarios=Nusuarios,Ndatos=Ndatos,score_total=round(score_total,2))

@app.route('/mapa')
def mapa():
    
    #Epicollect_GetData()
    #Agregar codigo
    MakeMap()
    return render_template('mapa.html')

@app.route('/mapeado')
def mapeado():
    return render_template('madrid_map.html')
@app.route('/irradiancia_mes')
def irradiancia_mes():
    
    return render_template('irradiancia_mes.html')

@app.route('/graficas')
def graficas():
    
    GraphMaker()
    return render_template('showGraphs.html')

@app.route('/datos')
def data():
    
    
    Epicollect_GetData()
    #DatosTabla = db.session.query(DatoPersona).order_by(func.substr(DatoPersona.fecha, 6, 2) + '-' + func.substr(DatoPersona.fecha, 9, 2)).all()
    DatosTabla = db.session.query(DatoPersona).order_by(DatoPersona.analisis.desc()).all()
    return render_template('datos.html', DatosTabla=DatosTabla)


@app.route('/leaderboard')
def leaderboard():
    #Epicollect_GetData()
       
    users = db.session.query(User).all()
    
    for user in users:
        email = user.email
        
        datosPuntos = db.session.query(DatoPersona).filter_by(username=email).all()
        user.score = 0
        for punto in datosPuntos:
            user.score += punto.analisis
            user.score = round(user.score, 2)
    
    db.session.commit()


    Users = db.session.query(User).order_by(User.score.desc()).all() #ordena los usuarios de mayor a menor puntuacion
    return render_template('leaderboard.html', Users=Users)

@app.route('/admin',methods=['GET', 'POST'])
def admin():
    
    if 'authenticated' in session:
        # El usuario ya está autenticado, mostrar la página admin
        mensajes = get_flashed_messages(with_categories=True)
        return render_template('admin.html', mensajes=mensajes)
    else:
        # El usuario no está autenticado, verificar la contraseña
        if request.method == 'POST':
            password = request.form['password']
            if password == 'admin10':
                session['authenticated'] = True
                return redirect(url_for('admin'))
            else:
                flash('Contraseña incorrecta', 'error')
    return render_template('admin.html')


from flask import send_file
import json,io

@app.route('/admin/registrar_sensor',methods=['GET', 'POST'])
def admin_register():
    if 'authenticated' in session:
        if request.method == 'POST':
            sensor_id = request.form['sensor_id']

            if not sensor_id.isdigit() or len(sensor_id) != 4 or sensor_id.startswith(('0')):
                return "Error: id_sensor debe ser un número entero de 4 dígitos"

            token=registrar_sensor(sensor_id)
            print(token)
            token_encriptado = generate_password_hash(token)
            sensor_aut = SensorAUT(id_sensor=sensor_id,token=token_encriptado)
            db.session.add(sensor_aut)
            db.session.commit()


            # Crear el contenido del archivo JSON
            data = {
                'sensor_id': sensor_id,
                'token': token
            }
            datos_json = json.dumps(data)
            
             # Establece los encabezados de la respuesta
            headers = {
                'Content-Disposition': f'attachment; filename=sensor_{sensor_id}.json',
                'Content-Type': 'application/json'
            }
            return datos_json, 200, headers
    
        # Devuelve la respuesta JSON con los encabezados establecidos
        
        
    return render_template('admin_registrarSensores.html')


@app.route('/admin/DatoSensor',methods=['GET', 'POST'])
def adminSensor():
    if 'authenticated' in session:
        datos = db.session.query(DatoSensor).all()
        if request.method == 'POST':
        
            atributo = request.form['atributo'].strip() 
            valor = request.form['valor'].strip() 
            EliminarDato(DatoSensor, atributo, valor)
            flash('Dato eliminado correctamente.', 'success')
            session.pop('authenticated', None)
            return redirect(url_for('admin'))
        return render_template('admin_sensor.html',datos=datos)
    else: 
        return redirect(url_for('admin'))


@app.route('/admin/users',methods=['GET', 'POST'])
def adminUser():
    if 'authenticated' in session:
        datos = db.session.query(User).all()
        if request.method == 'POST':
        
            atributo = request.form['atributo'].strip() 
            valor = request.form['valor'].strip() 
           
           
            if atributo == 'username':
                EliminarDato(Comment, 'username', valor)
                EliminarDato(User, atributo, valor)
            else:
                user_eliminar = db.session.query(User).filter_by(email=valor).first()
                print(user_eliminar)
                if user_eliminar:
                    EliminarDato(Comment, 'username', user_eliminar.username)
                    EliminarDato(User, atributo, valor)
            flash('Dato eliminado correctamente.', 'success')
            session.clear()
            session.pop('authenticated', None)
            
            
            return redirect(url_for('admin'))
        return render_template('admin_users.html',datos=datos)
    else: 
        return redirect(url_for('admin'))  
        

@app.route('/admin/comentarios',methods=['GET', 'POST'])
def adminComment():
    if 'authenticated' in session:
        datos = db.session.query(Comment).all()
        if request.method == 'POST':
        
            atributo = request.form['atributo'].strip() 
            valor = request.form['valor'].strip() 
            EliminarDato(Comment, atributo, valor)
            flash('Dato eliminado correctamente.', 'success')
            session.pop('authenticated', None)
            return redirect(url_for('admin'))
        return render_template('admin_comments.html',datos=datos)
    else: 
        return redirect(url_for('admin'))
        


@app.route('/admin/DatoPersona',methods=['GET', 'POST'])
def adminHuman():
    if 'authenticated' in session:
        datos = db.session.query(DatoPersona).all()
        if request.method == 'POST':
        
            atributo = request.form['atributo'].strip() 
            valor = request.form['valor'].strip() 
            EliminarDato(DatoPersona, atributo, valor)
            flash('Dato eliminado correctamente.', 'success')
            session.pop('authenticated', None)
            return redirect(url_for('admin'))
        return render_template('admin_humano.html',datos=datos)
    else: 
        return redirect(url_for('admin'))

users= {}

comments = []


@app.route('/feedback', methods=['GET', 'POST'])
def comment():
    comentarios = db.session.query(Comment).all()
   
    if 'username' in session:
        
        comentarios = db.session.query(Comment).order_by(Comment.date.desc()).all()

       
        if request.method == 'POST':
            comment = request.form['comment'].strip() # Elimina los espacios en blanco al principio y al final del comentario
            if comment and not comment.isspace(): # Verifica si el comentario no está vacío y no consiste solo en espacios en blanco
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M") # Formatea la fecha y hora actual
                comments.append({'username': session['username'], 'comment': comment, 'date': dt_string})
                hola = Comment(session['username'], comment, dt_string)
                db.session.add(hola)
                
                db.session.commit()
            return redirect(url_for('comment'))
            
                
        return render_template('feedback.html', comentarios=comentarios, username=session['username'])
    else:
        return redirect(url_for('login'))




@app.route('/signup', methods=['GET', 'POST'])  #Para registrarse
def signup():
    if request.method == 'POST':
        username = request.form['username'].lower()
        email = request.form['email'].lower()
        contraseña = request.form['password']
        error_message = None
        pfp = "static/userpfp/user-default.png"

        all_users = db.session.query(User).all()
    
        # Buscar el usuario con el nombre de usuario introducido
        user = None
        for u in all_users:
            if u.username == username:
                error_message = '*Nombre de usuario no disponible'
                return render_template('signup.html',error_message = error_message)
                break
            if u.email == email:
                error_message = '*Email no disponible'
                return render_template('signup.html',error_message = error_message)
                break

        password_policy = PasswordPolicy.from_names(
            length=5,  # Mínimo de 8 caracteres
            uppercase=0,  # Al menos una letra mayúscula
            numbers=1,  # Al menos un número
            nonletters=0,  # Al menos un carácter especial
        )
        if password_policy.test(contraseña):
            error_message = '*La contraseña no es lo suficientemente segura'
            #print("Has entrado al if")
            return render_template('signup.html', error_message=error_message)
        else:
            if contraseña == request.form['password_confirm']:
                #users[username] = {'email': email, 'contraseña': contraseña}
                pass_encrypt=generate_password_hash(contraseña)
                usuario = User(username,email,pass_encrypt,pfp)
                db.session.add(usuario)
                db.session.commit()
                print(contraseña )
                print("<<--- Separador --->>")
                print(pass_encrypt)
                return render_template('signup.html', success_message='Registro exitoso') # Aquí se pasa el parámetro de éxito
            else:
                error_message = '*Las contraseñas no coinciden'
                return render_template('signup.html',error_message = error_message)
        
    else:
        return render_template('signup.html')


# Definimos una ruta para la página de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if 'username' in session:
        # Obtener los datos del usuario de la sesión

        #date_registered = session['date_registered']

         # Pasar los datos del usuario a la plantilla , date_registered=date_registered
        return redirect('profile')
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']

        # Buscar todos los usuarios en la base de datos
        all_users = db.session.query(User).all()
    
        # Buscar el usuario con el nombre de usuario introducido
        user = None
        for u in all_users:
            if u.username == username:
                print(password)
                print("<<--- Separador --->>")
                print(u.password)
                if (check_password_hash(u.password, password)) == True:
                    user = u
                else:
                    return render_template('login.html', error_message='Contraseña incorrecta')
                break
    
       # print('username:', user.username)
        #print('email:', user.email)
       # print('pass:', user.password)
        

        if user is None:
            return render_template('login.html', error_message='Usuario no registrado')
        
        session['username'] = username
        print(session['username'])


        return redirect(url_for('perfil'))
    else:
        return render_template('login.html')

@app.route('/profile/delete',methods=['POST'])
def deleteProfile():

    username = session['username']
    

    user = db.session.query(User).filter_by(username=username).first()
    print(f"Deleting user with username {user.username}")
    db.session.delete(user)
    if user.profile_picture != "static/userpfp/user-default.png":
        os.remove(user.profile_picture)

    comments = db.session.query(Comment).filter_by(username=username).all()
    for comment in comments:
        db.session.delete(comment)


    db.session.commit()
    session.clear()
    return redirect(url_for('login'))

@app.route('/logout',methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/test2')
def tes2():
   if 'username' in session:
        mensajes = get_flashed_messages(with_categories=True)
        return render_template('subirDato.html',mensajes=mensajes)
   else:
        # Si el usuario no ha iniciado sesión, redirigir a la página de inicio de sesión
        return redirect(url_for('login'))


@app.route('/profile',methods=['GET','POST'])
def perfil():
    if 'username' in session:
        mensajes = get_flashed_messages(with_categories=True)
        username = session['username']
        
        user = db.session.query(User).filter_by(username=username).first()
        email = user.email
        if request.method == 'POST':
        # Manejar la carga de la imagen
            file = request.files['profile_picture']
            if file:
                # Asegurarse de que el nombre de archivo sea seguro
                filename = secure_filename(file.filename)
                # Guardar la imagen en el directorio 'userpfp' en el directorio 'static'
                file.save(os.path.join(app.config['PFP_UPLOAD_FOLDER'], filename))
                if user.profile_picture != "static/userpfp/user-default.png":
                    os.remove(user.profile_picture)

                # Actualizar la foto de perfil del usuario en la base de datos
                user.profile_picture = 'static/userpfp/' + filename
                db.session.commit()
                flash('La foto de perfil se ha actualizado correctamente.', 'success')
                return redirect(url_for('perfil'))
        # Obtener los datos del usuario de la sesión
    
      
        datosPuntos = db.session.query(DatoPersona).filter_by(username=email).all()
        user.score = 0
        for punto in datosPuntos:
            #print(user.score)
            #print(punto.analisis)
            user.score = user.score + punto.analisis   
       
        score = round(user.score,2)
        db.session.commit()   
        
        #date_registered = session['date_registered']
        #print(user.profile_picture)
        # Pasar los datos del usuario a la plantilla
        return render_template('profile.html', username=username, email=email,score=score,pfp=user.profile_picture,mensajes=mensajes)
    else:
        # Si el usuario no ha iniciado sesión, redirigir a la página de inicio de sesión
        return redirect(url_for('login'))

def obtener_perfil(username):
    user = db.session.query(User).filter_by(username=username).first()
    return user

@app.route('/<username>/mapa')
def UserMaper(username):


    perfil = obtener_perfil(username)
    sensores = db.session.query(SensorAUT).filter_by(username_asociado=username).all()
    MakeUserMap(perfil.username)

    return render_template('usermap.html')


@app.route('/<username>',methods=['GET'])
def usuario(username):
   
    perfil = obtener_perfil(username)
    sensores = db.session.query(SensorAUT).filter_by(username_asociado=username).all()
   
    return render_template('usuario.html', username=perfil.username,pfp=perfil.profile_picture,sensores=sensores)

@app.route('/device',methods=['GET','POST'])
def device():
    if 'username' in session:
        username = session['username']
        user = db.session.query(User).filter_by(username=username).first()
        sensores = db.session.query(SensorAUT).filter_by(username_asociado=username).all()
        return render_template('device.html',username=username,pfp=user.profile_picture,sensores=sensores)


@app.route('/device/register',methods=['GET','POST'])
def deviceregister():

        if request.method == 'POST':
            sensor_id = request.form['sensor_id']

            if not sensor_id.isdigit() or len(sensor_id) != 4 or sensor_id.startswith(('0')):
                return "Error: id_sensor debe ser un número entero de 4 dígitos"
            
            sensor = db.session.query(SensorAUT).filter_by(id_sensor=sensor_id).first()

            if sensor is not None:
                return "Error: Sensor ya registrado"
            username_asociado = session['username']
            token=registrar_sensor(sensor_id)
            print(token)
            token_encriptado = generate_password_hash(token)
            sensor_aut = SensorAUT(id_sensor=sensor_id,username_asociado=username_asociado,token=token_encriptado)
            db.session.add(sensor_aut)
            db.session.commit()


            # Crear el contenido del archivo JSON
            data = {
                'sensor_id': sensor_id,
                'token': token
            }
            datos_json = json.dumps(data)
            
             # Establece los encabezados de la respuesta
            headers = {
                'Content-Disposition': f'attachment; filename=sensor_{sensor_id}.json',
                'Content-Type': 'application/json'
            }
            return datos_json, 200, headers
        else:

            return render_template('registrarSensores.html')

@app.route('/uploadData', methods=['GET','POST']) #Para hacerlo desde la web
def uploadData():
    username = session['username']
    user = db.session.query(User).filter_by(username=username).first()
    
    if request.method == 'POST':
        email = user.email
        
        fecha = request.form['fecha']
        hora = request.form['hora']

        latitud = round(float(request.form['latitude'].replace(",",".")),6)
        longitud = round(float(request.form['longitude'].replace(",",".")),6)

        imagen = request.files['fotografia']

        if not imagen.filename:
            return "Error: no se ha enviado ningún archivo"
        filename = secure_filename(imagen.filename)
        extension = filename.rsplit('.', 1)[1].lower()
        if extension not in {'jpg', 'jpeg', 'png'}:
            return "Error: solo se permiten archivos de imagen (jpg, jpeg, png)"
        
       
        url=os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(url)
        if extension == 'jfif': # Descartado 
            print("es un jfif")
            with Image.open(url) as img:
                img = img.convert('RGB')
                new_filename = filename.rsplit('.', 1)[0] + '.jpg'
                filename = new_filename
                img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                print(url)
        else:
            imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        print(url)
        puntuacion = analyze_image(url)
        print(puntuacion)
        print("El dato del usuario ha llegado correctamente")
        #Crea un diccionario para cada usuario
        origen = "Web"

        Dato = DatoPersona(origen,username=email,fecha=fecha,hora=hora,latitud=latitud,longitud=longitud,analisis=puntuacion,url=os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db.session.add(Dato)
        db.session.commit()
        flash('El dato ha sido insertado correctamente', 'success')
        return redirect(url_for('tes2'))
        


from werkzeug.utils import secure_filename
import os
from sqlalchemy.orm.exc import NoResultFound

#flask run --host=0.0.0.0


@app.route('/addData', methods=['POST']) #Para sensores
def addData():

    id_sensor = request.form['id_sensor']

    token = request.form['token']
    
    try:
        sensor = db.session.query(SensorAUT).filter_by(id_sensor=id_sensor).one()
    except NoResultFound:
        return "Error: Sensor no autenticado"
  
    if  check_password_hash(sensor.token, token) != 1:
        return "Error: Sensor no autenticado"

    if not id_sensor.isdigit() or len(id_sensor) != 4 or id_sensor.startswith(('0')):
            return "Error: id_sensor debe ser un número entero de 4 dígitos"
    
    timestamp = request.form['timestamp']
    #fecha_hora_formateada = datetime.fromisoformat(timestamp_iso).strftime("%Y-%m-%dT%H:%M:%S")
    fecha_objeto = datetime.fromisoformat(timestamp)
    timestamp = fecha_objeto.strftime("%Y-%m-%dT%H:%M:%S")


    #Cambio las , a . para evitar posibles problemas
    latitud = request.form['latitud'].replace(",",".")
    longitud = request.form['longitud'].replace(",",".")
    orientacion = int(request.form['orientacion'])
    if orientacion >= 360: # 90 - Este, 180 - Sur, 270 - Oeste, 0 - Norte
        orientacion = orientacion-360
    
    try:
        latitud = float(latitud)
        longitud = float(longitud)#Valores maximos de latitud y long en la tierra
        if abs(latitud) > 90 or abs(longitud) > 180 or \
                    len(str(latitud).split('.')[-1]) < 6 or \
                    len(str(longitud).split('.')[-1]) < 6:
            raise ValueError()
    except ValueError:
        return "Error: latitud y longitud deben ser números decimales con al menos 6 decimales"
    

    tipo_medida = request.form['tipo_medida'] 
    
    #Depeniendo de lo que se envie, es un  tipo u otro (visto en Postman)
    if request.content_type.startswith('multipart/form-data'):

        
        valor = request.files['valor_medida']
        if not valor.filename:
            return "Error: no se ha enviado ningún archivo"
        filename = secure_filename(valor.filename)
        extension = filename.rsplit('.', 1)[1].lower()
        if extension not in {'jpg', 'jpeg', 'png'}:
            return "Error: solo se permiten archivos de imagen (jpg, jpeg, png)"
        
       
       
       
        valor.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print("El dato ha llegado bien el sensor que da imagen")
        #Crea un diccionario para cada usuario
        Dato = DatoSensor(id_sensor=id_sensor,timestamp=timestamp,latitud=latitud,longitud=longitud,orientacion=orientacion,tipo_medida=tipo_medida,valor=os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db.session.add(Dato)
        db.session.commit()
        
   
     #Depeniendo de lo que se envie, es un  tipo u otro (visto en Postman)
    if request.content_type == 'application/x-www-form-urlencoded':  
        valor = float(request.form['valor_medida'].replace(",","."))
        if tipo_medida == "SVF":
            if (valor) < 0 or (valor) > 1:
                return "Error: SVF debe estar entre 0 y 1"
        else:
            valor = float(request.form['valor_medida'].replace(",","."))
            cifras_significativas = 4
            #por ser float pone automaticamente el .0
            if len(str(valor).split('.', 1)[0])+len(str(valor).split('.', 1)[1]) < cifras_significativas: 
                raise ValueError("valor_medida debe tener  4 cifras significativas") 


        print("El dato ha llegado bien desde el sensor que da valor, tipo - ",tipo_medida)
        Dato = DatoSensor(id_sensor=id_sensor,timestamp=timestamp,latitud=latitud,longitud=longitud,orientacion=orientacion,tipo_medida=tipo_medida,valor=valor)
        db.session.add(Dato)
        db.session.commit() 
        
    return "Dato insertado correctamente"



import json 

def serialize_enum(obj): #Para poder poner en Json la enumeracion
    return obj.value

@app.route('/descargar-dato_irradiancia',methods=['GET'])
def descargar_dato():
    # Realiza la consulta a la base de datos para obtener los datos
    datos = db.session.query(DatoSensor).filter(DatoSensor.tipo_medida == "irradiancia").order_by(DatoSensor.id.asc()).all()

    # Transforma los objetos en diccionarios
    datos_dict = [dato.__dict__ for dato in datos]
    for dato in datos_dict:
        dato.pop('_sa_instance_state')  # Elimina el atributo '_sa_instance_state'
        dato['tipo_medida'] = serialize_enum(dato['tipo_medida'])  # Serializa el objeto TipoMedidaEnum

    # Convierte los datos en formato JSON
    datos_json = json.dumps(datos_dict)
    
    # Establece los encabezados de la respuesta
    headers = {
        'Content-Disposition': 'attachment; filename=datosIrradiancia.json',
        'Content-Type': 'application/json'
    }
    
    # Devuelve la respuesta JSON con los encabezados establecidos
    return datos_json, 200, headers


@app.route('/descargar-dato_SVF',methods=['GET'])
def descargar_dato_SVF():
    # Realiza la consulta a la base de datos para obtener los datos
    datos = db.session.query(DatoSensor).filter(DatoSensor.tipo_medida == "SVF").order_by(DatoSensor.id.asc()).all()

    # Transforma los objetos en diccionarios
    datos_dict = [dato.__dict__ for dato in datos]
    for dato in datos_dict:
        dato.pop('_sa_instance_state')  # Elimina el atributo '_sa_instance_state'
        dato['tipo_medida'] = serialize_enum(dato['tipo_medida'])  # Serializa el objeto TipoMedidaEnum

    # Convierte los datos en formato JSON
    datos_json = json.dumps(datos_dict)
    
    # Establece los encabezados de la respuesta
    headers = {
        'Content-Disposition': 'attachment; filename=datosSFV.json',
        'Content-Type': 'application/json'
    }
    
    # Devuelve la respuesta JSON con los encabezados establecidos
    return datos_json, 200, headers




if __name__ == '__main__':
    db.Base.metadata.create_all(db.engine)
    app.run(debug=True)    