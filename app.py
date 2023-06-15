from flask import Flask, render_template,request,redirect,url_for,session,flash,get_flashed_messages,make_response
#import folium
#import subprocess
#import os
from werkzeug.security import check_password_hash,generate_password_hash
from flask_session import Session
from datetime import datetime
from Pruebas.GraphMaker import GraphMaker
from MapMaker import MakeMap,MakeUserMap
from password_strength import PasswordPolicy
from Epicollect_GetData import Epicollect_GetData
from flask_jwt_extended import JWTManager,create_access_token


from claves import claveTokens, GOOGLE_ID, GOOGLE_SECRET, admin_pass
from Score import AsignarPuntos,calcular_puntuacion_entrada

from badges import haversine

from PIL import Image

from werkzeug.utils import secure_filename
import os
from sqlalchemy.orm.exc import NoResultFound

import db
from models import Comment,User,DatoSensor,DatoPersona,SensorAUT,Badge,UserBadge
#from bbdd_edit import EliminarDato
import uuid

import json

from flask_oauthlib.client import OAuth

import requests
import random
import string


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = claveTokens  # Clave secreta para firmar los tokens JWT -- secrets.token_hex(32)
jwt = JWTManager(app)

UPLOAD_FOLDER = 'static/datosFoto/' # Para guardar las imagenes enviadas

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PFP_UPLOAD_FOLDER'] = 'static/userpfp/' #Para almacenar las imagenes de perfil



# Claves secretas necesarias para la API de Google
app.config['GOOGLE_ID'] = GOOGLE_ID
app.config['GOOGLE_SECRET'] = GOOGLE_SECRET




Session(app)

# Funcion para obtener el usuario actual en un objeto de la clase User
def getUser():
    if 'username' in session:
        username = session['username']
        user = db.session.query(User).filter_by(username=username).first()
        return user
    return None


# Funcion para generar un token de autenticacion de forma aleatoria
def registrar_sensor(id_sensor):
    token = create_access_token(identity=id_sensor)
    return token

# Se encarga de generar las insignias
@app.cli.command("create_badges") # Este decorador permite usar la sentencia Flask create_badges desde la consola para realizar esta funcion y crear las insignias
def create_badges():
    bronze_badge = Badge(name='Bronze Badge', image_url="badges/bronze.png", descipcion="Obtenida por conseguir 20 puntos")
    silver_badge = Badge(name='Silver Badge', image_url="badges/silver.png", descipcion="Obtenida por conseguir 50 puntos")
    gold_badge = Badge(name='Gold Badge', image_url="badges/gold.png", descipcion="Obtenida por conseguir 100 puntos")

    bronze_colab = Badge(name='Bronze Collaboration Badge', image_url="badges/colabBro.png", descipcion="Obtenida por realizar 10 entradas manuales")
    silver_colab = Badge(name='Silver Collaboration Badge', image_url="badges/colabSilver.png", descipcion="Obtenida por realizar 25 entradas manuales")
    gold_colab = Badge(name='Gold Collaboration Badge', image_url="badges/colabGold.png", descipcion="Obtenida por realizar 50 entradas manuales")

    bronze_future = Badge(name='Bronze Futuristic Badge', image_url="badges/futBro.png", descipcion="Obtenida por realizar 50 entradas mediante sensores")
    silver_future = Badge(name='Silver Futuristic Badge', image_url="badges/futSilv.png", descipcion="Obtenida por realizar 100 entradas mediante sensores")
    gold_future = Badge(name='Gold Futuristic Badge', image_url="badges/futGold.png", descipcion="Obtenida por realizar 200 entradas mediante sensores")

    travel_badge = Badge(name='Travel Badge', image_url="badges/travel.png", descipcion="Obtenida al enviar dos datos con mucha distancia")
    perfectionist_badge = Badge(name='Perfectionist Badge', image_url="badges/perfect.png", descipcion="Obtenida al obtener una puntuación sobresaliente")

    db.session.add_all([bronze_badge, silver_badge, gold_badge, bronze_colab, silver_colab, gold_colab, bronze_future, silver_future, gold_future, travel_badge, perfectionist_badge])
    db.session.commit()


# Para borrar insignias a algun usuario en caso de necesidad
@app.cli.command("delete_badges")
def delete_badges():
    
    a = db.session.query(Badge).all()
    for entrada in a:
        db.session.delete(entrada)
 
    db.session.commit()
    #print('Badges created successfully.')

# Se encarga de asignar las insignias a los usuarios en caso de que cumplan las condiciones
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

# Test para asignar todas las insignias a un usuario
@app.cli.command("assignAll_badges")
#ef assignAll_badges():
#   user = db.session.query(User).filter_by(username="marki").first()
#
#   badges = db.session.query(Badge).all()
#
#   for badge in badges:
#       assign_badge(badge.name,user.username)

# Condiciones para asignar las insignias, si se cumple hace una llamda a assign_badge y asinga la insignia al usuario
def badge_giver(usuario):

    user = db.session.query(User).filter_by(username=usuario).first()
    
    if user.score >= 20 :
        assign_badge('Bronze Badge',usuario)
    if user.score >= 50 :
        assign_badge('Silver Badge',usuario)
    if user.score >= 100 :
        assign_badge('Gold Badge',usuario)

    nDatos = db.session.query(DatoPersona).filter_by(username=user.email).count()
    if nDatos >= 10 :
        assign_badge('Bronze Collaboration Badge',usuario)
    if nDatos >= 25 :
        assign_badge('Silver Collaboration Badge',usuario)
    if nDatos >= 50 :
        assign_badge('Gold Collaboration Badge',usuario)

    sensorUser = db.session.query(SensorAUT).filter_by(username_asociado=user.username).all()

    nFuture = 0
    for sensor in sensorUser:
        nFuture = nFuture + db.session.query(DatoSensor).filter_by(id_sensor=sensor.id_sensor).count()

    if nFuture >= 50 :
        assign_badge('Bronze Futuristic Badge',usuario)
    if nFuture >= 100 :
        assign_badge('Silver Futuristic Badge',usuario)
    if nFuture >= 200 :
        assign_badge('Gold Futuristic Badge',usuario)


    datosUser = db.session.query(DatoPersona).filter_by(username=user.email).all()
    for dato in datosUser:
        if dato.analisis > 9:
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
 


@app.route('/')  #La pagina principal.
def index():
    session.pop('authenticated', None)
    Nusuarios = db.session.query(User).count() 
    Ndatos = db.session.query(DatoPersona).count()
    score_total = 0
    datosPuntos = db.session.query(DatoPersona.analisis).all()

    for punto in datosPuntos:
            score_total += punto[0]

    return render_template('index.html',Nusuarios=Nusuarios,Ndatos=Ndatos,score_total=round(score_total,2))

@app.route('/mapa') #Actualiza los datos de Epicollect y muestra el mapa
def mapa():

    Epicollect_GetData()
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


@app.route('/datos/<int:page>') #Muestra los datos de cada usuario en diferentes paginas
def data(page=1):
    user = getUser()
    if user is not None:
        Epicollect_GetData()
        per_page = 10
        total_entries = db.session.query(DatoPersona).count()
        total_pages = total_entries // per_page + (total_entries % per_page > 0)
        offset = (page - 1) * per_page
        DatosTabla = db.session.query(DatoPersona).filter_by(username=user.email).order_by(DatoPersona.analisis.desc()).offset(offset).limit(per_page).all()
        return render_template('datos.html', DatosTabla=DatosTabla, page=page, total_pages=total_pages)
    else:
        return redirect(url_for('login'))



@app.route('/leaderboard') # Muestra una clasificación de los usuarios
def leaderboard():
    Epicollect_GetData()
    users = db.session.query(User).all()
    logros = db.session.query(UserBadge).all()
    insignias =  db.session.query(Badge).all()

    for user in users:
        db.session.commit()
        user.score = AsignarPuntos(user)
    db.session.commit()

    


    Users = db.session.query(User).order_by(User.score.desc()).all() #ordena los usuarios de mayor a menor puntuacion
    return render_template('leaderboard.html', Users=Users,logros=logros,insignias=insignias)

@app.route('/admin',methods=['GET', 'POST']) # Pagina de administrador
def admin():

    if 'authenticated' in session:
        # El usuario ya está autenticado, mostrar la página admin
        mensajes = get_flashed_messages(with_categories=True)
        return render_template('admin.html', mensajes=mensajes)
    else:
        # El usuario no está autenticado, verificar la contraseña
        if request.method == 'POST':
            password = request.form['password']
            if password == admin_pass:
                session['authenticated'] = True
                return redirect(url_for('admin'))
            else:
                flash('Contraseña incorrecta', 'error')
    return render_template('admin.html')

#Para visualizar los diferentes tipos de datos

@app.route('/admin/DatoSensor',methods=['GET', 'POST'])
def adminSensor():
    if 'authenticated' in session:
        datos = db.session.query(DatoSensor).all()
        return render_template('admin_sensor.html',datos=datos)
    else:
        return redirect(url_for('admin'))


@app.route('/admin/users',methods=['GET', 'POST'])
def adminUser():
    if 'authenticated' in session:
        datos = db.session.query(User).all()
        return render_template('admin_users.html',datos=datos)
    else:
        return redirect(url_for('admin'))


@app.route('/admin/comentarios',methods=['GET', 'POST'])
def adminComment():
    if 'authenticated' in session:
        datos = db.session.query(Comment).all()
        return render_template('admin_comments.html',datos=datos)
    else:
        return redirect(url_for('admin'))



@app.route('/admin/DatoPersona',methods=['GET', 'POST'])
def adminHuman():
    if 'authenticated' in session:
        datos = db.session.query(DatoPersona).all()
        return render_template('admin_humano.html',datos=datos)
    else:
        return redirect(url_for('admin'))



@app.route('/admin/sensoresAUT',methods=['GET', 'POST'])
def adminSensorsAUT():
    if 'authenticated' in session:
        datos = db.session.query(SensorAUT).all()
        return render_template('admin_sensoresAUT.html',datos=datos)
    else:
        return redirect(url_for('admin'))





@app.route('/feedback', methods=['GET', 'POST']) #Permite a los usuarios poner comentarios que puedan leer los Admin
def comment():
    if 'username' in session:

        comentarios = db.session.query(Comment).filter_by(username = session['username']).order_by(Comment.date.desc()).all()


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



from flask import jsonify

@app.route('/deleteComment', methods=['POST']) #Permite que un usuario borre un comentario previamente escrito
def deleteComment():
    data = request.get_json()
    comment_id = data.get('commentId')

    comment = db.session.query(Comment).filter_by(id=comment_id).first()
    if comment:
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'message': 'Comment deleted successfully', 'reload': True})
    else:
        return jsonify({'error': 'Comment not found'})



@app.route('/signup', methods=['GET', 'POST'])  #Permite registrarse al usuario
def signup():
    if request.method == 'POST':
        username = request.form['username'].lower()
        email = request.form['email'].lower()
        contraseña = request.form['password']
        error_message = None

        url_previa = request.referrer
        # Obtiene la url previa, sirve para diferencial si el usuario se registra con Google
    
        if url_previa == None:
            pfp = request.form['pfp']
        else:
            pfp = "userpfp/user-default.png"


        all_users = db.session.query(User).all()

        # Buscar si el nombre de usuario esta disponible
        for u in all_users:
            if u.username == username:
                error_message = '*Nombre de usuario no disponible'
                return render_template('signup.html',error_message = error_message)
            if u.email == email:
                error_message = '*Email no disponible'
                return render_template('signup.html',error_message = error_message)
            
        # Se definen caracteristicas de seguridad de la contraseña
        password_policy = PasswordPolicy.from_names(
            length=5,  # Mínimo de 5 caracteres
            uppercase=0,  
            numbers=1,  # Al menos un número
            nonletters=0,  
        )

        # Si no cumple las condiciones de seguridad, se pide que introduzca otra
        if password_policy.test(contraseña):
            error_message = '*La contraseña no es lo suficientemente segura'
            #print("Has entrado al if")
            return render_template('signup.html', error_message=error_message)
        else:

            if contraseña == request.form['password_confirm']: # Si la contraseña es segura y se confirma adecuadamente
                pass_encrypt=generate_password_hash(contraseña) # Se encripta la contraseña, para que no aparezca directamente en la BBDD
                usuario = User(username,email,pass_encrypt,pfp)
                db.session.add(usuario)
                db.session.commit()
                return render_template('signup.html', success_message='Registro exitoso') # Aquí se pasa el parámetro de éxito
            else: 
                error_message = '*Las contraseñas no coinciden'
                return render_template('signup.html',error_message = error_message)

    else:
        return render_template('signup.html')

@app.route('/check_registration') # Para checkear si un usuario esta registrado
def check_registration():
   
    if 'username' in session:
        is_registered = True  
    else:
        is_registered = False
    return jsonify({'isRegistered': is_registered})


# Inicio de sesión
@app.route('/login', methods=['GET', 'POST']) #Para que el usuario pueda iniciar sesión
def login():

    if 'username' in session: # Si ya ha iniciado sesion, se le redirige al perfil
        return redirect('profile')

    if request.method == 'POST': # Si se rellena el formulario de inicio de sesion
        username = request.form['username'].lower()
        password = request.form['password']

        all_users = db.session.query(User).all()

        # Buscar el usuario con el nombre de usuario introducido
        user = None
        for u in all_users:
            if u.username == username:

                if (check_password_hash(u.password, password)) == True: # Comprueba si la clave encriptada de la bbdd coincide con la contraseña introducida
                    user = u
                else:
                    return render_template('login.html', error_message='Contraseña incorrecta')
                break


        if user is None: # En caso de que el nombre de usuario no exista
            return render_template('login.html', error_message='Usuario no registrado')

        session['username'] = username

        return redirect(url_for('perfil'))
    else:
        return render_template('login.html')

#p.route('/profile/delete',methods=['POST'])~ Todo lo de borrar el perfil de usuario
# deleteProfile():
#
# username = session['username']
#
#
# user = db.session.query(User).filter_by(username=username).first()
# print(f"Deleting user with username {user.username}")
# db.session.delete(user)
# if user.profile_picture != "userpfp/user-default.png":
#     if os.path.isfile(user.profile_picture):
#         os.remove(user.profile_picture)
#
# comments = db.session.query(Comment).filter_by(username=username).all()
# for comment in comments:
#     db.session.delete(comment)
#
# sensAUT = db.session.query(SensorAUT).filter_by(username_asociado=username).all()
# for sens in sensAUT:
#     db.session.delete(sens)
#
# db.session.commit()
#
#
# filename = f'usermap_{username}.html'
# url = "templates/" + filename
# os.remove(url)
# session.clear()
#
# session.pop('username', None)
# return redirect(url_for('index'))

@app.route('/logout',methods=['POST']) # Permite que el usuario cierre sesion
def logout():
    session.clear() # Limpia la sesion
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/uploaddata',methods=['GET']) # Permite realizar entradas de datos desde la WEB
def uploaddata():
   if 'username' in session:
        mensajes = get_flashed_messages(with_categories=True)
        return render_template('subirDato.html',mensajes=mensajes)
   else:
        # Si el usuario no ha iniciado sesión, redirigir a la página de inicio de sesión
        return redirect(url_for('login'))
   

@app.route('/uploadData', methods=['GET','POST']) # Formulario asociado a la URL anterior
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
        if extension not in {'jpg', 'jpeg', 'png'}: # Solo admite estos formatos
            return "Error: solo se permiten archivos de imagen (jpg, jpeg, png)"

        filename = str(uuid.uuid4()) + '.' + extension
        url=os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
        imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        ruta  = 'datosFoto/' + filename # Añade el nombre del archivo a la ruta 
 
        origen = "Web"

        Dato = DatoPersona(origen,username=email,fecha=fecha,hora=hora,latitud=latitud,longitud=longitud,analisis=0,url= ruta)

        Puntos = calcular_puntuacion_entrada(Dato,DatoPersona) # Se puntua la entrada 

        Dato = DatoPersona(origen,username=email,fecha=fecha,hora=hora,latitud=latitud,longitud=longitud,analisis=Puntos,url= ruta)

        db.session.add(Dato)
        db.session.commit()
        flash('El dato ha sido insertado correctamente', 'success')
        return redirect(url_for('uploaddata'))
    
# Para que el usuario pueda decidir si muestra el mapa al resto de usuarios
@app.route('/mostrar_mapa', methods=['POST']) 
def mostrar_mapa():

    user = getUser()
    if   user.show_map == 0:
        user.show_map = 1
    elif user.show_map == 1:
        user.show_map = 0
    
    db.session.commit()
    return redirect(url_for('perfil'))


@app.route('/profile',methods=['GET','POST']) # Muestra el perfil del usuario, con su información
def perfil():
    if 'username' in session:
        mensajes = get_flashed_messages(with_categories=True)

        user = getUser()

        # Permite cambiar la imagen de perfil
        if request.method == 'POST':
       
            file = request.files['profile_picture']
            if file:
                # Asegurarse de que el nombre de archivo sea seguro
                filename = secure_filename(file.filename)
                # Guardar la imagen en el directorio 'userpfp' en el directorio 'static'
                file.save(os.path.join(app.config['PFP_UPLOAD_FOLDER'], filename))
                if user.profile_picture != "userpfp/user-default.png": # Si no es la imagen por defecto, se borra la imagen anterior
                    ruta_archivo = "static/" + user.profile_picture
                    os.remove(ruta_archivo) 

                # Actualizar la foto de perfil del usuario en la base de datos
                user.profile_picture = 'userpfp/' + filename
                db.session.commit()
                flash('La foto de perfil se ha actualizado correctamente.', 'success')
                return redirect(url_for('perfil'))
        # Obtener los datos del usuario de la sesión
        user.score = AsignarPuntos(user)
         
        db.session.commit()
        badge_giver(user.username) # Comprueba si el usuario cumple condiciones de las insignias y las entrega
        badges = db.session.query(UserBadge).filter_by(user_id=user.username).all()
        insignias =  db.session.query(Badge).all()
        

        # Pasar los datos del usuario a la plantilla
        return render_template('profile.html', user=user,mensajes=mensajes,badges=badges,insignias = insignias)
    else:
        # Si el usuario no ha iniciado sesión, redirigir a la página de inicio de sesión
        return redirect(url_for('login'))

def obtener_perfil(username): #Para obtener un usuario a partir de su username
    user = db.session.query(User).filter_by(username=username).first()
    return user

@app.route('/<username>/mapa',methods=['GET']) # Para mostrar los mapas de los usuarios que no tengan iniciada sesion
def UserMaper(username):
    perfil = obtener_perfil(username)
    MakeUserMap(perfil.username) # Crea/Actualiza el mapa del usuario

    return render_template(f'usermap_{username}.html')



@app.route('/profile/<username>',methods=['GET']) # Permite visualizar datos del resto de usuarios
def usuario(username):
    perfil = obtener_perfil(username)
    sensores = db.session.query(SensorAUT).filter_by(username_asociado=username).all()

    if 'username' in session:
        if session['username'] == perfil.username:
            return redirect(url_for('perfil'))

    logros = db.session.query(UserBadge).filter_by(user_id=username).all()
    insignias =  db.session.query(Badge).all()

    return render_template('usuario.html', perfil = perfil,sensores=sensores,logros=logros,insignias = insignias)

@app.route('/device/<username>',methods=['GET','POST']) # Permite al usuario ver sus dispositivos asociados y crear nuevos (max 3)
def device(username):
    if session['username'] == obtener_perfil(username).username:
        username = session['username']
        user = db.session.query(User).filter_by(username=username).first()
        sensores = db.session.query(SensorAUT).filter_by(username_asociado=username).all()
        return render_template('device.html',username=username,pfp=user.profile_picture,sensores=sensores)
    else:
        return redirect(url_for('login'))


@app.route('/device/register',methods=['GET','POST']) # Para crear nuevos dispositivos asociados
def deviceregister():
        mensajes = get_flashed_messages(with_categories=True)
        if request.method == 'POST':
            
            user = getUser()

            
            
            nSensor = db.session.query(SensorAUT).filter_by(username_asociado=user.username).count()

            # El maximo de sensores es 3
            if nSensor < 3:
                sensor_id = user.id * 1000 + (1 + nSensor ) # +1 porque nSensor puede ser 0 1 2
                username_asociado = user.username
                token=registrar_sensor(sensor_id) # Crea un token asociado el sensor_id
                token_encriptado = generate_password_hash(token) # Encripta el token para que no aparezca en la BBDD
                sensor_aut = SensorAUT(id_sensor=sensor_id,username_asociado=username_asociado,token=token_encriptado)
                db.session.add(sensor_aut)
                db.session.commit()
                flash('Sensor registrado correctamente', 'success')
            
            else:
                flash('Ya no puedes registrar más sensores', 'error')
                return redirect(url_for('device', username=user.username))
                

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
            
            return datos_json, 200, headers,  # Se descarga automaticamente un JSON que contiene el sensor_id y el token
        else:
            return render_template('registrarSensores.html',mensajes=mensajes)
        
        


from flask import Flask, redirect, url_for,request
from flask_oauthlib.client import OAuth

# Para gestionar el registro con Google

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



@app.route('/GoogleLogin') # Para poder redirigir a la pagina de registro de google
def GoogleLogin():
    return google.authorize(callback=url_for('authorized', _external=True))





def generar_contraseña():
    longitud = 10
    caracteres = string.ascii_letters + string.digits

    contraseña = ''.join(random.choice(caracteres) for _ in range(longitud))
    return contraseña



# Una vez Google permite el acceso, se realiza el proceso de registro o inicio de sesion
@app.route('/authorized') 
def authorized():


    resp = google.authorized_response() # Se comprueba que Google autoriza
    if resp is None:
        return 'Error al autorizar.'
    
    # Se obtienen diferentes datos de la cuenta de google
    access_token = resp['access_token']
    session['access_token'] = access_token
    userinfo = google.get('userinfo')
    email = userinfo.data['email']
    username = email.split('@')[0] # El username en la WEB sera el email antes del @
    password = generar_contraseña()
    if db.session.query(User).filter_by(username=username).first() is not None: # Comprueba que no este registrado ya
        session['username'] = username
        return redirect(url_for('perfil'))

    else:
        pfp = userinfo.data['picture']
        session['username'] = username

        datos = {
            'username':username,
            'email' : email,
            'pfp' : pfp,
            'password':password,
            'password_confirm': password
        }
        url = 'http://photovolta.pythonanywhere.com/signup'
        requests.post(url, data=datos) # Hace POST al formulario de registro
        return redirect(url_for('perfil'))


@google.tokengetter
def get_google_oauth_token():
    return session.get('access_token')




@app.route('/addData', methods=['POST']) #Para enviar entradas via API con dispositivos registrados
def addData():

    id_sensor = request.form['id_sensor']

    token = request.headers.get('token')

    # Se comprueba que el sensor esta registrado
    try:
        sensor = db.session.query(SensorAUT).filter_by(id_sensor=id_sensor).one()
    except NoResultFound:
        return "Error: Sensor no autenticado"

    # Comprueba si el token introducido es correcto
    if  check_password_hash(sensor.token, token) != 1:
        return "Error: Sensor no autenticado"

    # Obtiene los datos de la peticion
    timestamp = request.form['timestamp']
    fecha_objeto = datetime.fromisoformat(timestamp)
    timestamp = fecha_objeto.strftime("%Y-%m-%dT%H:%M:%S")

    #Cambio las , a . para evitar posibles problemas
    latitud = request.form['latitud'].replace(",",".")
    longitud = request.form['longitud'].replace(",",".")

    # Se comprueban algunos datos
    orientacion = int(request.form['orientacion'])
    if orientacion >= 360: # 90 - Este, 180 - Sur, 270 - Oeste, 0 - Norte
        orientacion = orientacion-360
    inclinacion = int(request.form['inclinacion'])
    if inclinacion > 180: #Por ejemplo
        inclinacion = inclinacion-180
    try:
        latitud = float(latitud)
        longitud = float(longitud)#Valores maximos de latitud y long en la tierra
        if abs(latitud) > 90 or abs(longitud) > 180 or len(str(latitud).split('.')[-1]) < 6 or len(str(longitud).split('.')[-1]) < 6:
            raise ValueError()
    except ValueError:
        return "Error: latitud y longitud deben ser números decimales con al menos 6 decimales"


    tipo_medida = request.form['tipo_medida']
    # Devuelve un mensaje de que se ha enviado bien el dato, indicando el tipo
    mensaje = f"Dato insertado correctamente tipo  -  {tipo_medida}"
    response = make_response(mensaje)
    response.status_code = 200

    #Depeniendo de lo que se envie, es un  tipo u otro (visto en Postman)
    if request.content_type.startswith('multipart/form-data'): # Este es para los que contengan imganes


        valor = request.files['valor_medida']
        if not valor.filename:
            return "Error: no se ha enviado ningún archivo"
        filename = secure_filename(valor.filename)
        # Se comprueba que la extension es adecuada (solo imagenes)
        extension = filename.rsplit('.', 1)[1].lower()
        if extension not in {'jpg', 'jpeg', 'png'}:
            return "Error: solo se permiten archivos de imagen (jpg, jpeg, png)"

        valor.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        ruta  = 'datosFoto/' + filename # Añade el nombre del archivo a la ruta 
        Dato = DatoSensor(id_sensor=id_sensor,timestamp=timestamp,latitud=latitud,longitud=longitud,orientacion=orientacion,inclinacion=inclinacion,tipo_medida=tipo_medida,valor=ruta)
        db.session.add(Dato)
        db.session.commit()


    #Dependiendo de lo que se envie, es un  tipo u otro (visto en Postman)
    if request.content_type == 'application/x-www-form-urlencoded': # Si solo se envian caracteres
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


# Se permite la descarga de datos enviados via API

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

    # Devuelve los datos en un JSON
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

    # Devuelve los datos en un JSON
    return datos_json, 200, headers



# Para iniciar la aplicacion Flask, tiene que ir al final del codigo
# Si no hay bbdd, se crea

if __name__ == '__main__':
    db.Base.metadata.create_all(db.engine)
    app.run(debug=True)