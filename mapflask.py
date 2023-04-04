from flask import Flask, render_template,request,redirect,url_for,session
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


app = Flask(__name__)
app.secret_key = "clave_secreta"
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


@app.route('/')
def index():
    return render_template('index.html')

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
    DatosTabla = db.session.query(DatoTabla).all()
    return render_template('datos.html', DatosTabla=DatosTabla)



users= {}

comments = []





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

@app.route('/logout',methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/test')
def test():
    return(users)


from flask import render_template, session, redirect, url_for

@app.route('/profile')
def perfil():
    if 'username' in session:
        # Obtener los datos del usuario de la sesión
        username = session['username']
       
        user = db.session.query(User).filter_by(username=username).first()
        email = user.email
        #date_registered = session['date_registered']

        # Pasar los datos del usuario a la plantilla , date_registered=date_registered
        return render_template('profile.html', username=username, email=email)
    else:
        # Si el usuario no ha iniciado sesión, redirigir a la página de inicio de sesión
        return redirect(url_for('login'))




#def run():
#    hola = Comment('Juan','Que locura HERMANO LOOOOOOOL ;)')
#    db.session.add(hola)
#    db.session.commit()
    

if __name__ == '__main__':
    db.Base.metadata.create_all(db.engine)
    app.run(debug=True)