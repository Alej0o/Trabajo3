from flask import render_template, request, redirect, session
import psycopg2
from flask import send_file
import uuid
from werkzeug.utils import secure_filename
from os import path
@app.route("/css/<archivocss>")
def css_link(archivocss):
    return send_from_directory(os.path.join('templates/proyecto/css'),archivocss)

@app.route('/')
def inicio():
    return render_template('proyecto/index.html')

@app.route('/registro')
def reg():
    return render_template('proyecto/registro.html')

@app.route('/director/')
def director_index():
    return render_template('director/index.html')
  @app.route('/n')
def indefinido_index():
    return render_template('/proyecto/indefinido.html')

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
