import os
from flask import Flask, flash, url_for
from flask import render_template, request, redirect, session
import psycopg2
from flask import send_file
import uuid
from werkzeug.utils import secure_filename
from os import path
from datetime import datetime
from flask import send_from_directory

app=Flask(__name__)
app.secret_key="steveen"


connection=psycopg2.connect(dbname="proysemilleros", user="postgres", password="st3v3")


@app.route("/css/<archivocss>")
def css_link(archivocss):
    return send_from_directory(os.path.join('templates/proyecto/css'),archivocss)
@app.route('/login', methods=['POST'])
def login():
    email=request.form["email"]
    password=request.form["password"]

    cursor=connection.cursor()
    cursor.execute("select * from usuarios where email=%s and password=%s",[email,password])
    usuario=cursor.fetchone()

    if usuario is not None:
        session['email']=email
        session['name']=usuario[1]
        session['id_rol']=usuario[4]

        if session['id_rol']==1:
            return render_template('director/index.html')
        elif session['id_rol']==2:
            return redirect(url_for('coordinador_index'))
        elif session['id_rol']==3:
            return redirect(url_for('semillerista_index'))
        elif session['id_rol']==4:
            return redirect(url_for('indefinido_index'))
    else:
        return render_template('proyecto/index.html', message=" Las credenciales nos son correctas")

@app.route('/')
def inicio():
    return render_template('proyecto/index.html')

@app.route('/registro')
def reg():
    return render_template('proyecto/registro.html')
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('inicio'))

@app.route('/director/')
def director_index():
    return render_template('director/index.html')
  @app.route('/n')
def indefinido_index():
    return render_template('/proyecto/indefinido.html')
@app.route('/coordinador/integrantes')
def coordinador_integrantes():

    email=session['email']
    cursor=connection.cursor()
    cursor.execute("select * from semillero where email='{0}'".format(email))
    sem=cursor.fetchall()
    connection.commit()

    cursor=connection.cursor()
    cursor.execute("select idus,username,email from usuarios where id_rol=4")
    integrantes=cursor.fetchall()
    connection.commit()
    print(integrantes)

    idsem=str(sem[0][0])
    cursor=connection.cursor()
    cursor.execute("select * from semest where idsem={0}".format(idsem))
    semest=cursor.fetchall()
    connection.commit()

    return render_template('coordinador/integrantes.html', integrantes=integrantes,sem=sem,semest=semest)
    
@app.route('/director/semilleros')
def director_semilleros():

    cursor=connection.cursor()
    cursor.execute("select * from semillero")
    semilleros=cursor.fetchall()
    connection.commit()
    print(semilleros)

    return render_template('director/director.html', semilleros=semilleros)
    
@app.route('/coordinador/')
def coordinador_index():
    
    email=session['email']
    cursor=connection.cursor()
    cursor.execute("select * from semillero where email='{0}'".format(email))
    sem=cursor.fetchall()
    connection.commit()

    return render_template('coordinador/index.html', sem=sem)
@app.route('/semillerista/')
def semillerista_index():
    email=session['email']
    cursor=connection.cursor()
    cursor.execute("select idsem from semest where email='{0}'".format(email))
    semi=cursor.fetchall()
    connection.commit()

    _idsem=str(semi[0][0])
    cursor=connection.cursor()
    cursor.execute("select nombre from semillero as s inner join semest as se on se.idsem=s.idsem where se.idsem={0}".format(_idsem))
    idsemi=cursor.fetchall()
    connection.commit()

    return render_template('semillerista/index.html',semi=semi,idsemi=idsemi)

@app.route('/director/semilleros/guardar', methods=['POST'])
def director_semilleros_guardar():

    _nombre=request.form['txtNombre']
    _ubicacion=request.form['txtUbicacion']
    _email=request.form['email']
    _idrol=2

    cursor=connection.cursor()
    cursor.execute("select * from usuarios where email=%s",[_email])
    usuario=cursor.fetchone()

    if usuario is not None:

        cursor=connection.cursor()
        sql="insert into semillero(nombre, ubicacion, email) values(%s,%s,%s)"
        datos=(_nombre,_ubicacion,_email)
        cursor.execute(sql,datos)
        connection.commit

        cursor=connection.cursor()
        sql="update usuarios set id_rol={0} where email='{1}'".format(_idrol,_email)
        datos1=(_idrol)
        cursor.execute(sql,datos1)
        connection.commit
        flash(" Registro exitoso")
        return redirect(url_for('director_semilleros'))
    flash(" El correo ingresado no esta registrado")
    return redirect(url_for('director_semilleros'))

@app.route('/coordinador/integrantes/agregar', methods=['POST'])
def coord_agregar_integrante():

    _idsem=request.form['idsem']
    _email=request.form['email']
    _idrol=3
    _us=request.form['us']

    cursor=connection.cursor()
    sql="insert into semest(idsem,email,username) values(%s,%s,%s)"
    datos=(_idsem,_email,_us)
    cursor.execute(sql,datos)
    connection.commit()

    cursor=connection.cursor()
    sql="update usuarios set id_rol={0} where email='{1}'".format(_idrol,_email)
    datos1=(_idrol)
    cursor.execute(sql,datos1)
    connection.commit

    flash(" Se agrego con exito") 

    return redirect('/coordinador/integrantes')

@app.route('/registro/usuario', methods=['POST'])
def registro():
    nu=request.form['nu']
    email=request.form['email']
    password=request.form['pass']
    id_rol=4

    cursor=connection.cursor()
    sql="insert into usuarios (username,email,password,id_rol) values(%s,%s,%s,%s)"
    datos=(nu,email,password,id_rol)
    cursor.execute(sql,datos)
    connection.commit()

    flash(" Cuenta Registrada")
    return redirect(url_for('reg'))

#METODOS DESCARGA DESDE AQUI 
#Funcion que recorre todos los archivos almacenados en la carpeta (archivos)  
def listaArchivos():
    urlFiles = 'static/archivos'
    return (os.listdir(urlFiles))
     
#Creando un Decorador
@app.route('/coordinador/Coordproyectos/descargar/<string:nombreFoto>', methods=['GET','POST'])
def descargar_Archivo(nombreFoto=''):
    basepath = path.dirname (_file_) 
    url_File = path.join (basepath, 'static/archivos', nombreFoto)
    #send_file toma 2 parametros, el primero será la ruta del archivo y el
    # 2 será as_attachment=True porque deseamos que el archivo sea descargable.
    resp =  send_file(url_File, as_attachment=True)
    return resp    

#Redireccionando cuando la página no existe
@app.errorhandler(404)
def not_found(error):
    return 'Ruta no encontrada'

#METODOS NUEVO PROYECTO DESDE AQUI
@app.route('/coordinador/Coordproyectos', methods=['GET', 'POST'])
def semillero_coord():  
    
    idsem=request.form['idsem']
    cursor = connection.cursor()
    cursor.execute("select * from proyecto where idsem={0}".format(idsem))
    tasks = cursor.fetchall()
    connection.commit()

    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in tasks:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()

    return render_template('coordinador/Coordproyectos.html', tasks=insertObject,list_Photos = listaArchivos())

#MAIN
@app.route('/coordinador/Coordproyectos/archivos/<ver>')
def archivos(ver):
    print(ver)
    return send_from_directory(os.path.join('static/archivos'),ver)

#METODOS CREAR PROYECTO
@app.route('/semillerista/proyecto', methods=['GET', 'POST'])
def tasks():

    email=session['email']
    cursor=connection.cursor()
    cursor.execute("select idsem from semest where email='{0}'".format(email))
    semi=cursor.fetchall()
    connection.commit()

    email = session['email']
    cursor = connection.cursor()
    cursor.execute("select * from proyecto where email='{0}'".format(email))
    tasks = cursor.fetchall()
    connection.commit()

    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in tasks:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()

    return render_template('semillerista/proyecto.html', tasks=insertObject,semi=semi)

@app.route('/new-task', methods=['GET', 'POST'])
def newTask():
    if request.method == 'POST':
            if(request.files['archivo']):
                #Script para archivo
                file     = request.files['archivo']
                basepath = path.dirname (__file__) #La ruta donde se encuentra el archivo actual
                filename = secure_filename(file.filename) #Nombre original del archivo
                
                #capturando extensión del archivo ejemplo: (.png, .jpg, .pdf ...etc)
                extension           = path.splitext(filename)[1]
                nuevoNombreFile     = uuid.uuid4().hex + extension
        
                upload_path = path.join (basepath, 'static/archivos', nuevoNombreFile) 
                file.save(upload_path)

    idsem=request.form['idsem']
    email=session['email']
    title = request.form['title']
    description = request.form['description']
    email = session['email']
    tiproy=request.form['tiproy']
    d = datetime.now()
    dateTask = d.strftime("%Y/%m/%d %H:%M:%S")
    archivo=nuevoNombreFile
    
    cursor=connection.cursor()
    sql = "INSERT INTO proyecto (email, titulo, descripcion, fecha, idsem, archivo,tipoproy) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    data = (email, title, description, dateTask, idsem, archivo, tiproy)
    cursor.execute(sql, data)
    connection.commit()

    flash(" Proyecto creado")
    
    return redirect(url_for('tasks', list_Photos = listaArchivos()))

@app.route('/semillerista/proyecto/eliminar', methods=['GET','POST'])
def deleteTask(nombreFoto=''):
    _id=request.form['id']

    cursor =connection.cursor()
    cursor.execute("select archivo from proyecto where idproy={0}".format(_id))
    proyecto = cursor.fetchall()
    connection.commit()

    if os.path.exists("static/archivos/"+str(proyecto[0][0])):
       os.unlink("static/archivos/"+str(proyecto[0][0]))

    cursor =connection.cursor()
    cursor.execute("delete from proyecto where idproy={0}".format(_id))
    connection.commit()

    return redirect(url_for('tasks'))


if _name=='__main_':
    app.run(debug=True)
