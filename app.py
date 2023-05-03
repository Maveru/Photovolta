from flask import Flask, render_template,request,redirect,url_for,session,flash,get_flashed_messages
#import folium
#import subprocess
#import os
#from werkzeug.security import check_password_hash,generate_password_hash
from flask_session import Session
from datetime import datetime
from GraphMaker import GraphMaker
from MapMaker import MakeMap
from password_strength import PasswordPolicy


#from Epicollect_GetData import DatosTabla
#from jinja2 import Environment

#from Epicollect_GetData import Epicollect_GetData,MakeMap

import db
from models import Comment,User,DatoImagen,DatoValor,DatoEpicollect
#from sqlalchemy import func


#flask --app .\mapflask.py run --host 0.0.0.0
app = Flask(__name__)
app.secret_key = "clave_secreta"
UPLOAD_FOLDER = 'static/datosFoto/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PFP_UPLOAD_FOLDER'] = 'static/userpfp/'
Session(app)


@app.route('/')
def index():
    Nusuarios = db.session.query(User).count()#No se si pasar los registrados en la pagina o los que han mandado datos a Epicollect
   
    Ndatos = db.session.query(DatoEpicollect).count()

    users = db.session.query(User).all()
    score_total = 0
    
    datosPuntos = db.session.query(DatoEpicollect.analisis).all()
    
    for punto in datosPuntos:
            score_total += punto[0]
            print(score_total)

    


    return render_template('index.html',Nusuarios=Nusuarios,Ndatos=Ndatos,score_total=round(score_total,2))

@app.route('/mapa')
def mapa():
    #os.system('python Epicollect_GetData.py') 
    #Epicollect_GetData()
    #Agregar codigo
    MakeMap()
    return render_template('mapa.html')

@app.route('/mapeado')
def mapeao():
    #os.system('python Epicollect_GetData.py') 
    
    return render_template('madrid_map.html')
@app.route('/irradiancia_mes')
def irradiancia_mes():
    #os.system('python Epicollect_GetData.py') 
    
    return render_template('irradiancia_mes.html')

@app.route('/graficas')
def graficas():
    #os.system('python Epicollect_GetData.py') 
    GraphMaker()
    return render_template('showGraphs.html')

@app.route('/datos')
def data():
    
    
    #Epicollect_GetData()
    #DatosTabla = db.session.query(DatoEpicollect).order_by(func.substr(DatoEpicollect.fecha, 6, 2) + '-' + func.substr(DatoEpicollect.fecha, 9, 2)).all()
    DatosTabla = db.session.query(DatoEpicollect).order_by(DatoEpicollect.analisis.desc()).all()
    return render_template('datos.html', DatosTabla=DatosTabla)


@app.route('/leaderboard')
def leaderboard():
    #Epicollect_GetData()
       
    users = db.session.query(User).all()
    
    for user in users:
        email = user.email
        
        datosPuntos = db.session.query(DatoEpicollect).filter_by(username=email).all()
        user.score = 0
        for punto in datosPuntos:
            user.score += punto.analisis
            user.score = round(user.score, 2)



    Users = db.session.query(User).order_by(User.score.desc()).all() #ordena los usuarios de mayor a menor puntuacion
    return render_template('leaderboard.html', Users=Users)



users= {}

comments = []


#poner una tabla que solo muestre los usuarios sus puntos e insignias/

#user_id = request.args.get('user_id') # Obtener el id del usuario desde la consulta de la URL
 #               user = db.session.query(User).first() # Buscar al usuario por su id
  #              user.score += 1 # Aumentar la puntuación del usuario en 1


# Definimos una ruta para procesar el formulario
@app.route('/feedback', methods=['GET', 'POST'])
def comment():
    comentarios = db.session.query(Comment).all()
   
    if 'username' in session:
        #comentarios = db.session.query(Comment).order_by(func.substr(Comment.date, 6, 2) + '-' + func.substr(Comment.date, 9, 2)).all()
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
                usuario = User(username,email,contraseña,pfp)
                db.session.add(usuario)
                db.session.commit()
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
                user = u
                break

       # print('username:', user.username)
        #print('email:', user.email)
       # print('pass:', user.password)
        

        if user is None:
            return render_template('login.html', error_message='Usuario no registrado')
        
        if user.password != password:
            return render_template('login.html', error_message='Contraseña incorrecta')
        
        session['username'] = username
        print(session['username'])


        return redirect(url_for('perfil'))


        if username in users and users[username]['contraseña'] == password:
                session['username'] = username
                return redirect(url_for('comment'))
        else:
            error_message = '*Datos de inicio de sesión incorrectos'
            return render_template('login.html',error_message = error_message)
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
    
      
        datosPuntos = db.session.query(DatoEpicollect).filter_by(username=email).all()
        user.score = 0
        for punto in datosPuntos:
            #print(user.score)
            #print(punto.analisis)
            user.score = user.score + punto.analisis   
       
        score = round(user.score,2)
        db.session.commit()   
        
        #date_registered = session['date_registered']
        print(user.profile_picture)
        # Pasar los datos del usuario a la plantilla
        return render_template('profile.html', username=username, email=email,score=score,pfp=user.profile_picture)
    else:
        # Si el usuario no ha iniciado sesión, redirigir a la página de inicio de sesión
        return redirect(url_for('login'))



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
        
       
       
       
        imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print("El dato ha llegado bien el sensor que da imagen")
        #Crea un diccionario para cada usuario
        Dato = DatoEpicollect(username=email,fecha=fecha,hora=hora,latitud=latitud,longitud=longitud,analisis=0,url=os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db.session.add(Dato)
        db.session.commit()
        flash('El dato ha sido insertado correctamente', 'success')
        return redirect(url_for('tes2'))
        


from werkzeug.utils import secure_filename
import os

@app.route('/addData', methods=['POST']) #Para sensores
def addData():

    id_sensor = request.form['id_sensor']
    if not id_sensor.isdigit() or len(id_sensor) != 4 or id_sensor.startswith(('0')):
            return "Error: id_sensor debe ser un número entero de 4 dígitos"
    
    fecha = request.form['fecha'].replace("/","-")
    hora = request.form['hora']
    
    #fecha_hora_formateada = datetime.fromisoformat(timestamp_iso).strftime("%Y-%m-%dT%H:%M:%S")
    
    #Cambio las , a . para evitar posibles problemas
    latitud = request.form['latitud'].replace(",",".")
    longitud = request.form['longitud'].replace(",",".")
    try:
        latitud = float(latitud)
        longitud = float(longitud)#Valores maximos de latitud y long en la tierra
        if abs(latitud) > 90 or abs(longitud) > 180 or \
                    len(str(latitud).split('.')[-1]) < 6 or \
                    len(str(longitud).split('.')[-1]) < 6:
            raise ValueError()
    except ValueError:
        return "Error: latitud y longitud deben ser números decimales con al menos 6 decimales"
    


    #Depeniendo de lo que se envie, es un  tipo u otro (visto en Postman)
    if request.content_type.startswith('multipart/form-data'):

        
        imagen = request.files['imagen']
        if not imagen.filename:
            return "Error: no se ha enviado ningún archivo"
        filename = secure_filename(imagen.filename)
        extension = filename.rsplit('.', 1)[1].lower()
        if extension not in {'jpg', 'jpeg', 'png'}:
            return "Error: solo se permiten archivos de imagen (jpg, jpeg, png)"
        
       
       
       
        imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print("El dato ha llegado bien el sensor que da imagen")
        #Crea un diccionario para cada usuario
        Dato = DatoImagen(id_sensor=id_sensor,fecha=fecha,hora=hora,latitud=latitud,longitud=longitud,imagen=os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db.session.add(Dato)
        db.session.commit()
        
   
     #Depeniendo de lo que se envie, es un  tipo u otro (visto en Postman)
    if request.content_type == 'application/x-www-form-urlencoded':  
      
        valor = float(request.form['valor_medida'].replace(",","."))
        cifras_significativas = 4
        
        #por ser float pone automaticamente el .0
        if len(str(valor).split('.', 1)[0])+len(str(valor).split('.', 1)[1]) < cifras_significativas: 
            raise ValueError("valor_medida debe tener  4 cifras significativas") 


        print("El dato ha llegado bien desde el sensor que da valor")
        Dato = DatoValor(id_sensor=id_sensor,fecha=fecha,hora=hora,latitud=latitud,longitud=longitud,valor_medida=valor)
        db.session.add(Dato)
        db.session.commit() 
        
    return "Dato insertado correctamente"




if __name__ == '__main__':
    db.Base.metadata.create_all(db.engine)
    app.run(debug=True)    