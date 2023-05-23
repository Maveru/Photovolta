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


from badges import haversine

from PIL import Image
from flask_jwt_extended import create_access_token

from werkzeug.utils import secure_filename
import os
from sqlalchemy.orm.exc import NoResultFound

import db
import os
from models import Comment,User,DatoSensor,DatoPersona,SensorAUT,Badge,UserBadge
from bbdd_edit import EliminarDato

from flask import send_file
import json

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = '685b9e7b32a529df7051e23c4c490808f783e4abbc7ea933cdb502385d694ecf'  # Clave secreta para firmar los tokens JWT -- secrets.token_hex(32)
jwt = JWTManager(app)
app.secret_key = "clave_secreta"
UPLOAD_FOLDER = 'static/datosFoto/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PFP_UPLOAD_FOLDER'] = 'static/userpfp/'

app.config['GOOGLE_ID'] = '480090602143-naqm1phl4lgn81pt44d0350omrr9rg3e.apps.googleusercontent.com'
app.config['GOOGLE_SECRET'] = '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'




Session(app)

sensores_autenticados = {}


def registrar_sensor(id_sensor):
    token = create_access_token(identity=id_sensor)
    sensores_autenticados[id_sensor] = token
    return token


@app.cli.command("create_badges")
def create_badges():
    
    bronze_badge = Badge(name='Bronze Badge',image_url = "badges/bronze.png",descipcion = "Obtenida por conseguir 20 puntos")
    silver_badge = Badge(name='Silver Badge',image_url = "badges/silver.png",descipcion = "Obtenida por conseguir 50 puntos")
    gold_badge = Badge(name='Gold Badge',image_url = "badges/gold.png",descipcion = "Obtenida por conseguir 100 puntos")
    travel_badge = Badge(name='Travel Badge',image_url = "badges/travel.png",descipcion = "Obtenida al enviar dos datos con mucha distancia")
    perfectionist_badge=Badge(name='Perfectionist Badge',image_url = "badges/perfect.png",descipcion = "Obtenida al obtener la maxima puntuación en una medida")
    db.session.add_all([bronze_badge, silver_badge, gold_badge,travel_badge,perfectionist_badge])
    db.session.commit()
    #print('Badges created successfully.')

@app.cli.command("delete_badges")
def delete_badges():
    
    a = db.session.query(Badge).all()
    for entrada in a:
        db.session.delete(entrada)
 
    db.session.commit()
    #print('Badges created successfully.')

#@app.cli.command("assign_badge")
def assign_badge(NombreInsignia,usuario):
    user = db.session.query(User).filter_by(username=usuario).first()  # Obtén el usuario al que deseas asignar la insignia
   
    if user is None:
        print('El usuario no existe.')
        return

    badge_name = NombreInsignia   # Nombre de la insignia que deseas asignar

    badge = db.session.query(Badge).filter_by(name=badge_name).first()
    if badge is None:
        print('La insignia no existe.')
        return

    if db.session.query(UserBadge).filter_by(user_id=user.username, badge_id=badge.name).first():
        print('El usuario ya tiene esta insignia asignada.')
        return

    user_badge = UserBadge(user_id=user.username, badge_id=badge.name)
    db.session.add(user_badge)
    db.session.commit()
    print(f'Insignia "{badge.name}" asignada al usuario "{user.username}".')


def badge_giver(usuario):

    user = db.session.query(User).filter_by(username=usuario).first()
    
    if user.score >= 10 :
        assign_badge('Bronze Badge',usuario)
    if user.score >= 50 :
        assign_badge('Silver Badge',usuario)
    if user.score >= 100 :
        assign_badge('Gold Badge',usuario)

    datosUser = db.session.query(DatoPersona).filter_by(username=user.email).all()
    for dato in datosUser:
        if dato.analisis == 10:
            assign_badge('Perfectionist Badge',usuario)
            break

    for i in range(len(datosUser)):
        for j in range(i+1, len(datosUser)):
            dato1 = datosUser[i]
            dato2 = datosUser[j]

            distancia = haversine(dato1.latitud, dato1.longitud, dato2.latitud, dato2.longitud)

            if distancia >= 500:
                # Asignar la insignia al usuario, ya que la condición se cumple
                assign_badge('Travel Badge',usuario)
                break




@app.route('/')
def index():
    session.pop('authenticated', None)
    Nusuarios = db.session.query(User).count() #No se si pasar los registrados en la pagina o los que han mandado datos a Epicollect
    Ndatos = db.session.query(DatoPersona).count()
    score_total = 0
    datosPuntos = db.session.query(DatoPersona.analisis).all()

    for punto in datosPuntos:
            score_total += punto[0]

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


@app.route('/datos/<int:page>')
def data(page=1):
    Epicollect_GetData()
    # DatosTabla = db.session.query(DatoPersona).order_by(func.substr(DatoPersona.fecha, 6, 2) + '-' + func.substr(DatoPersona.fecha, 9, 2)).all()
    per_page = 10
    total_entries = db.session.query(DatoPersona).count()
    total_pages = total_entries // per_page + (total_entries % per_page > 0)
    offset = (page - 1) * per_page
    DatosTabla = db.session.query(DatoPersona).order_by(DatoPersona.analisis.desc()).offset(offset).limit(per_page).all()
    return render_template('datos.html', DatosTabla=DatosTabla, page=page, total_pages=total_pages)


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



@app.route('/admin/sensoresAUT',methods=['GET', 'POST'])
def adminSensorsAUT():
    if 'authenticated' in session:
        datos = db.session.query(SensorAUT).all()
        if request.method == 'POST':

            atributo = request.form['atributo'].strip()
            valor = request.form['valor'].strip()
            EliminarDato(SensorAUT, atributo, valor)
            flash('Dato eliminado correctamente.', 'success')
            session.pop('authenticated', None)
            return redirect(url_for('admin'))
        return render_template('admin_sensoresAUT.html',datos=datos)
    else:
        return redirect(url_for('admin'))




users= {}


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

                comentario = Comment(session['username'], comment, dt_string)
                db.session.add(comentario)

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

        url_previa = request.referrer
        if url_previa == None:
            pfp = request.form['pfp']
        else:
            pfp = "userpfp/user-default.png"


        all_users = db.session.query(User).all()

        # Buscar el usuario con el nombre de usuario introducido
        user = None
        for u in all_users:
            if u.username == username:
                error_message = '*Nombre de usuario no disponible'
                return render_template('signup.html',error_message = error_message)
            if u.email == email:
                error_message = '*Email no disponible'
                return render_template('signup.html',error_message = error_message)

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
                return render_template('signup.html', success_message='Registro exitoso') # Aquí se pasa el parámetro de éxito
            else:
                error_message = '*Las contraseñas no coinciden'
                return render_template('signup.html',error_message = error_message)

    else:
        return render_template('signup.html')


# Inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():

    if 'username' in session:
        return redirect('profile')

    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']

        all_users = db.session.query(User).all()

        # Buscar el usuario con el nombre de usuario introducido
        user = None
        for u in all_users:
            if u.username == username:

                if (check_password_hash(u.password, password)) == True:
                    user = u
                else:
                    return render_template('login.html', error_message='Contraseña incorrecta')
                break


        if user is None:
            return render_template('login.html', error_message='Usuario no registrado')

        session['username'] = username

        return redirect(url_for('perfil'))
    else:
        return render_template('login.html')

@app.route('/profile/delete',methods=['POST'])
def deleteProfile():

    username = session['username']


    user = db.session.query(User).filter_by(username=username).first()
    print(f"Deleting user with username {user.username}")
    db.session.delete(user)
    if user.profile_picture != "userpfp/user-default.png":
        if os.path.isfile(user.profile_picture):
            os.remove(user.profile_picture)

    comments = db.session.query(Comment).filter_by(username=username).all()
    for comment in comments:
        db.session.delete(comment)


    db.session.commit()
    session.clear()

    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/logout',methods=['POST'])
def logout():
    session.clear()
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/uploaddata',methods=['GET'])
def uploaddata():
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
                if user.profile_picture != "userpfp/user-default.png":
                    ruta_archivo = "static/" + user.profile_picture
                    os.remove(ruta_archivo)

                # Actualizar la foto de perfil del usuario en la base de datos
                user.profile_picture = 'userpfp/' + filename
                db.session.commit()
                flash('La foto de perfil se ha actualizado correctamente.', 'success')
                return redirect(url_for('perfil'))
        # Obtener los datos del usuario de la sesión

        
        datosPuntos = db.session.query(DatoPersona).filter_by(username=email).all()
        user.score = 0
        for punto in datosPuntos:
            user.score = user.score + punto.analisis

     
        score = round(user.score,2)
        db.session.commit()
        badge_giver(username)
        badges = db.session.query(UserBadge).filter_by(user_id=username).all()
        insignias =  db.session.query(Badge).all()
        

        # Pasar los datos del usuario a la plantilla
        return render_template('profile.html', username=username, email=email,score=score,pfp=user.profile_picture,mensajes=mensajes,badges=badges,insignias = insignias)
    else:
        # Si el usuario no ha iniciado sesión, redirigir a la página de inicio de sesión
        return redirect(url_for('login'))

def obtener_perfil(username):
    user = db.session.query(User).filter_by(username=username).first()
    return user

@app.route('/<username>/mapa',methods=['GET'])
def UserMaper(username):
    perfil = obtener_perfil(username)
    MakeUserMap(perfil.username)

    return render_template(f'usermap_{username}.html')

@app.route('/profile/<username>',methods=['GET'])
def usuario(username):
    perfil = obtener_perfil(username)
    sensores = db.session.query(SensorAUT).filter_by(username_asociado=username).all()

    if 'username' in session:
        if session['username'] == perfil.username:
            return redirect(url_for('perfil'))

    badges = db.session.query(UserBadge).filter_by(user_id=username).all()
    insignias =  db.session.query(Badge).all()

    return render_template('usuario.html', username=perfil.username,pfp=perfil.profile_picture,sensores=sensores,badges=badges,insignias = insignias)

@app.route('/device/<username>',methods=['GET','POST'])
def device(username):
    if session['username'] == obtener_perfil(username).username:
        username = session['username']
        user = db.session.query(User).filter_by(username=username).first()
        sensores = db.session.query(SensorAUT).filter_by(username_asociado=username).all()
        return render_template('device.html',username=username,pfp=user.profile_picture,sensores=sensores)
    else:
        return redirect(url_for('login'))


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
            #print(token)
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
import uuid
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

        filename = str(uuid.uuid4()) + '.' + extension
        url=os.path.join(app.config['UPLOAD_FOLDER'], filename)
        #print(url)
        if extension == 'jfif': # Descartado
            print("es un jfif")
            with Image.open(url) as img:
                img = img.convert('RGB')
                new_filename = filename.rsplit('.', 1)[0] + '.jpg'
                filename = new_filename
                img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                url = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        else:
            imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        ruta  = 'datosFoto/' + filename
        print(ruta)
        puntuacion = analyze_image(url)

        print("El dato del usuario ha llegado correctamente")
        #Crea un diccionario para cada usuario
        origen = "Web"

        Dato = DatoPersona(origen,username=email,fecha=fecha,hora=hora,latitud=latitud,longitud=longitud,analisis=puntuacion,url= ruta)
        db.session.add(Dato)
        db.session.commit()
        flash('El dato ha sido insertado correctamente', 'success')
        return redirect(url_for('uploaddata'))

from flask import Flask, redirect, url_for,request
from flask_oauthlib.client import OAuth

oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key=app.config['GOOGLE_ID'],
    consumer_secret=app.config['GOOGLE_SECRET'],
    request_token_params={
        'scope': 'https://www.googleapis.com/auth/userinfo.email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth'
)



@app.route('/GoogleLogin')
def GoogleLogin():
    return google.authorize(callback=url_for('authorized', _external=True))




import random
import string

def generar_contraseña():
    longitud = 10
    caracteres = string.ascii_letters + string.digits

    contraseña = ''.join(random.choice(caracteres) for _ in range(longitud))
    return contraseña


import requests
@app.route('/authorized')
def authorized():


    resp = google.authorized_response()
    if resp is None:
        return 'Error al autorizar.'

    access_token = resp['access_token']
    session['access_token'] = access_token
    userinfo = google.get('userinfo')
    email = userinfo.data['email']
    username = email.split('@')[0]
    password = generar_contraseña()
    if db.session.query(User).filter_by(username=username).first() is not None:
        session['username'] = username
        return redirect(url_for('perfil'))

    else:
        pfp = userinfo.data['picture']


        datos = {
            'username':username,
            'email' : email,
            'pfp' : pfp,
            'password':password,
            'password_confirm': password
        }
        url = 'http://photovolta.pythonanywhere.com/signup'
        requests.post(url, data=datos)
        return redirect(url_for('login'))


@google.tokengetter
def get_google_oauth_token():
    return session.get('access_token')

#flask run --host=0.0.0.0

from flask import make_response
@app.route('/addData', methods=['POST']) #Para sensores
def addData():

    id_sensor = request.form['id_sensor']

    token = request.headers.get('token')

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
    inclinacion = int(request.form['inclinacion'])
    if inclinacion > 180: #Por ejemplo
        inclinacion = inclinacion-180
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



    mensaje = f"Dato insertado correctamente tipo  -  {tipo_medida}"
    response = make_response(mensaje)
    response.status_code = 200

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

        Dato = DatoSensor(id_sensor=id_sensor,timestamp=timestamp,latitud=latitud,longitud=longitud,orientacion=orientacion,inclinacion=inclinacion,tipo_medida=tipo_medida,valor=os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db.session.add(Dato)
        db.session.commit()


    #Dependiendo de lo que se envie, es un  tipo u otro (visto en Postman)
    if request.content_type == 'application/x-www-form-urlencoded':
        valor = float(request.form['valor_medida'].replace(",","."))
        if tipo_medida == "SVF":
            tipo_medida = tipo_medida.upper()
            if (valor) < 0 or (valor) > 1:
                return "Error: SVF debe estar entre 0 y 1"
        elif tipo_medida == "irradiancia":
            valor = float(request.form['valor_medida'].replace(",","."))
            cifras_significativas = 4
            #por ser float pone automaticamente el .0
            if len(str(valor).split('.', 1)[0])+len(str(valor).split('.', 1)[1]) < cifras_significativas:
                return "valor_medida debe tener  4 cifras significativas"



        Dato = DatoSensor(id_sensor=id_sensor,timestamp=timestamp,latitud=latitud,longitud=longitud,orientacion=orientacion,inclinacion=inclinacion,tipo_medida=tipo_medida,valor=valor)
        db.session.add(Dato)
        db.session.commit()

    return response


def serialize_enum(obj): #Para poder poner en Json la enumeracion
    return obj.value

@app.route('/subirdatos',methods=['GET'])
def subirdatos():
    return render_template('subirDato.html')

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