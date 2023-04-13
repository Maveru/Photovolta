from flask import Flask, render_template,request,redirect,url_for,session,flash
import folium
import subprocess
import os
from werkzeug.security import check_password_hash,generate_password_hash
from flask_session import Session
from datetime import datetime
#from Epicollect_GetData import DatosTabla
from jinja2 import Environment

import db
from models import Comment,User,DatoTabla
from sqlalchemy import func
app = Flask(__name__)
app.secret_key = "clave_secreta"
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


@app.route('/')
def index():
    Nusuarios = db.session.query(User).count()#No se si pasar los registrados en la pagina o los que han mandado datos a Epicollect
   
    Ndatos = db.session.query(DatoTabla).count()

    users = db.session.query(User).all()
    score_total = 0
    
    datosPuntos = db.session.query(DatoTabla.analisis).all()
    
    for punto in datosPuntos:
            score_total += punto[0]
            print(score_total)

    


    return render_template('index.html',Nusuarios=Nusuarios,Ndatos=Ndatos,score_total=round(score_total,2))

@app.route('/mapa')
def mapa():
    os.system('python Epicollect_GetData.py') # Agregar la llamada a tu programa aquí
    
    
    return render_template('mapa.html')
@app.route('/mapeado')
def mapeao():
    #os.system('python Epicollect_GetData.py') # Agregar la llamada a tu programa aquí
    
    return render_template('madrid_map.html')

@app.route('/datos')
def data():
    #DatosTabla = db.session.query(DatoTabla).order_by(func.substr(DatoTabla.fecha, 6, 2) + '-' + func.substr(DatoTabla.fecha, 9, 2)).all()
    DatosTabla = db.session.query(DatoTabla).order_by(DatoTabla.analisis.desc()).all()
    return render_template('datos.html', DatosTabla=DatosTabla)


@app.route('/leaderboard')
def leaderboard():
       
    users = db.session.query(User).all()
    
    for user in users:
        email = user.email
        
        datosPuntos = db.session.query(DatoTabla).filter_by(username=email).all()
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
        comentarios = db.session.query(Comment).all()
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

        all_users = db.session.query(User).all()
    
        # Buscar el usuario con el nombre de usuario introducido
        user = None
        for u in all_users:
            if u.username == username:
                error_message = '*Nombre de usuario no disponible'
                return render_template('signup.html',error_message = error_message)
                break
            if u.email == email:
                error_message = '*Email ya registrado'
                return render_template('signup.html',error_message = error_message)
                break

            
        if contraseña == request.form['password_confirm']:
            #users[username] = {'email': email, 'contraseña': contraseña}
            usuario = User(username,email,contraseña)
            db.session.add(usuario)
            db.session.commit()
            return redirect(url_for('login')) 
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


        return redirect(url_for('comment'))


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


@app.route('/test')
def test():
   return render_template('test.html')


from flask import render_template, session, redirect, url_for

@app.route('/profile')
def perfil():
    if 'username' in session:
        # Obtener los datos del usuario de la sesión
        username = session['username']
       
        user = db.session.query(User).filter_by(username=username).first()
        email = user.email
      
        datosPuntos = db.session.query(DatoTabla).filter_by(username=email).all()
        user.score = 0
        for punto in datosPuntos:
            print(user.score)
            print(punto.analisis)
            user.score = user.score + punto.analisis   
       
        score = user.score
        db.session.commit()   
        
        #date_registered = session['date_registered']

        # Pasar los datos del usuario a la plantilla
        return render_template('profile.html', username=username, email=email,score=score)
    else:
        # Si el usuario no ha iniciado sesión, redirigir a la página de inicio de sesión
        return redirect(url_for('login'))



if __name__ == '__main__':
    db.Base.metadata.create_all(db.engine)
    app.run(debug=True)