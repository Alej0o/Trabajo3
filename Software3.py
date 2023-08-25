import os
from flask import Flask, flash, url_for
from flask import render_template, request, redirect, session
import psycopg2
from datetime import datetime
from flask import send_from_directory
#descarga
from flask import send_file
import uuid
from werkzeug.utils import secure_filename
from os import path


app=Flask(__name__)
app.secret_key="steveen"

connection=psycopg2.connect(dbname="proysemilleros", user="postgres", password="st3v3")

@app.route("/css/<archivocss>")
def css_link(archivocss):
    return send_from_directory(os.path.join('templates/proyecto/css'),archivocss)

#Registro, Inicio de sesión, Cerrar sesión

@app.route('/')
def inicio():
    return render_template('proyecto/index.html')

@app.route('/registro')
def reg():
    return render_template('proyecto/registro.html')

@app.route('/registro/usuario', methods=['POST'])
def registro():
    nu=request.form['nu']
    email=request.form['email']
    password=request.form['pass']
    id_rol=4

    cursor=connection.cursor()
    cursor.execute("select * from usuarios where email=%s or password=%s",[email,password])
    exist=cursor.fetchone()

    if exist is not None:
        flash(" El email ya esta registrado",'error')
        return redirect(url_for('reg'))
    cursor=connection.cursor()
    sql="insert into usuarios (username,email,password,id_rol) values(%s,%s,%s,%s)"
    datos=(nu,email,password,id_rol)
    cursor.execute(sql,datos)
    connection.commit()

    flash(" Cuenta Registrada",'success')
    return redirect(url_for('reg'))


@app.route('/login', methods=['POST'])
def login():
    email=request.form["email"]
    password=request.form["password"]

    cursor=connection.cursor()
    cursor.execute("select * from usuarios where email=%s and password=%s",[email,password])
    usuario=cursor.fetchone()

    if usuario is not None:
        session["login"]=True
        session['email']=email
        session['idus']=usuario[0]
        session['name']=usuario[1]
        session['id_rol']=usuario[4]

        if session['id_rol']==1 and session['login']:
            return render_template('director/index.html')
        elif session['id_rol']==2 and session['login']:
            return redirect(url_for('coordinador_index'))
        elif session['id_rol']==3 and session['login']:
            return redirect(url_for('semillerista_index'))
        elif session['id_rol']==4 and session['login']:
            return redirect(url_for('indefinido_index'))
    else:
        return render_template('proyecto/index.html', message=" Las credenciales nos son correctas")
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('inicio'))

#Inicio Roles

@app.route('/n')
def indefinido_index():

    if not "login" in session:
        return redirect("/")
    
    return render_template('/proyecto/indefinido.html')

@app.route('/director/')
def director_index():

    if not "login" in session:
        return redirect("/")
    
    return render_template('director/index.html')


@app.route('/coordinador/')
def coordinador_index():

    if not "login" in session:
        return redirect("/")
    
    email=session['email']
    cursor=connection.cursor()
    cursor.execute("select * from semillero where email='{0}'".format(email))
    sem=cursor.fetchall()
    connection.commit()

    return render_template('coordinador/index.html', sem=sem)

@app.route('/semillerista/')
def semillerista_index():

    if not "login" in session:
        return redirect("/")
    
    email=session['email']
    cursor=connection.cursor()
    cursor.execute("select idsem from semest as sm inner join usuarios as us on sm.idus=us.idus where email='{0}';".format(email))
    semi=cursor.fetchall()
    connection.commit()

    _idsem=str(semi[0][0])
    cursor=connection.cursor()
    cursor.execute("select distinct on(nombre) nombre from semillero as s inner join semest as se on se.idsem=s.idsem where se.idsem={0}".format(_idsem))
    idsemi=cursor.fetchall()
    connection.commit()

    return render_template('semillerista/index.html',semi=semi,idsemi=idsemi)

#CRUD Semillero

@app.route('/director/semilleros')
def director_semilleros():

    if not "login" in session:
        return redirect("/")

    cursor=connection.cursor()
    cursor.execute("select * from semillero")
    semilleros=cursor.fetchall()
    connection.commit()
    print(semilleros)

    return render_template('director/director.html', semilleros=semilleros)

@app.route('/director/semilleros/guardar', methods=['POST'])
def director_semilleros_guardar():

    if not "login" in session:
        return redirect("/")

    _nombre=request.form['txtNombre']
    _ubicacion=request.form['txtUbicacion']
    _email=request.form['email']
    _idrol=2

    cursor=connection.cursor()
    cursor.execute("select * from usuarios where email=%s",[_email])
    usuario=cursor.fetchone()

    cursor=connection.cursor()
    cursor.execute("select * from semillero where email=%s",[_email])
    repetido=cursor.fetchone()

    if repetido is not None:
        flash(" El usuario ya cuenta con un semillero asignado",'error1')
        return redirect(url_for('director_semilleros'))
    elif usuario is not None:
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
        flash(" Registro exitoso",'success')
        return redirect(url_for('director_semilleros'))
    flash(" El correo ingresado no esta registrado", 'error')
    return redirect(url_for('director_semilleros'))

@app.route('/director/semilleros/editar/<string:id>', methods=['POST'])
def director_semilleros_editar(id):

    if not "login" in session:
        return redirect("/")
    
    _nombre=request.form['txtNombre']
    _ubicacion=request.form['txtUbicacion']
    _emailnuevo=request.form['emailnuevo']
    _emailactual=request.form['emailactual']
    _idrolnuevo=2
    _idrolactual=4

    cursor=connection.cursor()
    cursor.execute("select * from usuarios where email=%s",[_emailnuevo])
    usuario=cursor.fetchone()

    cursor=connection.cursor()
    cursor.execute("select * from semillero where email=%s",[_emailnuevo])
    repetido=cursor.fetchone()

    if repetido is not None:
        flash(" El usuario ya cuenta con un semillero asignado",'erroreditsem')
        return redirect(url_for('director_semilleros'))
    elif usuario is not None:
        if _emailnuevo==_emailactual:
            cursor = connection.cursor()
            sql = "UPDATE semillero SET nombre = %s, ubicacion = %s, email = %s WHERE idsem = %s"
            data = (_nombre, _ubicacion, _emailnuevo, id)
            cursor.execute(sql, data)
            connection.commit()
            flash(" Semillero Actualizado",'success2')
            return redirect(url_for('director_semilleros'))
        elif _emailnuevo!=_emailactual:
            cursor = connection.cursor()
            sql = "UPDATE semillero SET nombre = %s, ubicacion = %s, email = %s WHERE idsem = %s"
            data = (_nombre, _ubicacion, _emailnuevo, id)
            cursor.execute(sql, data)
            connection.commit()

            cursor=connection.cursor()
            sql="update usuarios set id_rol={0} where email='{1}'".format(_idrolnuevo,_emailnuevo)
            datos1=(_idrolnuevo)
            cursor.execute(sql,datos1)
            connection.commit()

            cursor=connection.cursor()
            cursor.execute("update usuarios set id_rol={0} where email='{1}'".format(_idrolactual,_emailactual))
            connection.commit()
            flash(" Semillero Actualizado",'success2')
            return redirect(url_for('director_semilleros'))
    flash(" El correo ingresado no esta registrado", 'error5')
    return redirect(url_for('director_semilleros'))

@app.route('/director/semilleros/eliminar', methods=['POST'])
def director_semilleros_eliminar():

    if not "login" in session:
        return redirect("/")
    
    _id=request.form['txtID']
    cursor=connection.cursor()
    cursor.execute("delete from semillero where idsem={0}".format(_id))
    connection.commit()

    email=request.form['email']
    _idrol=4
    cursor=connection.cursor()
    cursor.execute("update usuarios set id_rol={0} where email='{1}'".format(_idrol,email))
    connection.commit

    flash(" Semillero Eliminado",'success1')

    return redirect('/director/semilleros')

#CRUD Cuenta 

@app.route('/cuenta')
def cuenta():

    if not "login" in session:
        return redirect("/")
    
    email=session['email']
    cursor=connection.cursor()
    cursor.execute("select * from usuarios where email='{0}'".format(email))
    cuenta=cursor.fetchall()
    connection.commit()

    return render_template('/cuenta/cuenta.html',cuenta=cuenta)

@app.route('/cuenta/editarcuenta', methods=['POST'])
def editar_cuenta():

    if not "login" in session:
        return redirect("/")

    email=session['email']
    us=request.form['txtus']
    pas=request.form['txtPass']

    cursor=connection.cursor()
    cursor.execute("select * from usuarios where email='{0}'".format(email))
    cuenta=cursor.fetchall()
    connection.commit()

    usactual=str(cuenta[0][1])
    pasactual=str(cuenta[0][3])

    if us==usactual and pas==pasactual:
        flash(" Datos similares",'error_cuenta')
        return redirect(url_for('cuenta'))
    else:
        cursor = connection.cursor()
        sql = "UPDATE usuarios SET username = %s, password = %s WHERE email = %s"
        data = (us, pas, email)
        cursor.execute(sql, data)
        connection.commit()
        flash(" Datos Actualizados",'success_cuenta')
        return redirect(url_for('cuenta'))

@app.route('/cuenta/eliminarcuenta', methods=['POST'])
def eliminar_cuenta():

    if not "login" in session:
        return redirect("/")
    
    email=session['email']
    idus=session['idus']
    rol=session['id_rol']
    newemail=''

    if rol==4:
        cursor=connection.cursor()
        cursor.execute("delete from usuarios where email='{0}'".format(email))
        connection.commit()
    elif rol==3:
        cursor=connection.cursor()
        cursor.execute("delete from intproy as ip where idus='{0}'".format(idus))
        connection.commit()

        cursor=connection.cursor()
        cursor.execute("delete from semest where idus='{0}'".format(idus))
        connection.commit()

        cursor=connection.cursor()
        cursor.execute("delete from usuarios where idus='{0}'".format(idus))
        connection.commit()

    elif rol==2:
        cursor = connection.cursor()
        sql = "UPDATE semillero SET email = %s WHERE email = %s"
        data = (newemail, email)
        cursor.execute(sql, data)
        connection.commit()

        cursor=connection.cursor()
        cursor.execute("delete from usuarios where email='{0}'".format(email))
        connection.commit()

    elif rol==1:
        cursor=connection.cursor()
        cursor.execute("delete from usuarios where email='{0}'".format(email))
        connection.commit()

    return redirect(url_for('inicio'))


# Coordinador Agregar/Consultar/Quitar Integrante

@app.route('/coordinador/integrantes')
def coordinador_integrantes():

    if not "login" in session:
        return redirect("/")

    email=session['email']
    cursor=connection.cursor()
    cursor.execute("select * from semillero where email='{0}'".format(email))
    sem=cursor.fetchall()
    connection.commit()

    idsemillero=sem[0][0]

    cursor=connection.cursor()
    cursor.execute("select idus,username,email from usuarios where id_rol=4")
    integrantes=cursor.fetchall()
    connection.commit()
    print(integrantes)

    cursor=connection.cursor()
    cursor.execute("select u.idus,username,email from usuarios as u inner join semest as sm on u.idus=sm.idus where idsem={0}".format(idsemillero))
    semest=cursor.fetchall()
    connection.commit()

    return render_template('coordinador/integrantes.html', integrantes=integrantes,sem=sem,semest=semest)

@app.route('/coordinador/integrantes/agregar', methods=['POST'])
def coord_agregar_integrante():

    if not "login" in session:
        return redirect("/")

    _idsem=request.form['idsem']
    _idus=request.form['idus']
    _idrol=3

    cursor=connection.cursor()
    sql="insert into semest(idsem,idus) values(%s,%s)"
    datos=(_idsem,_idus)
    cursor.execute(sql,datos)
    connection.commit()

    cursor=connection.cursor()
    sql="update usuarios set id_rol={0} where idus='{1}'".format(_idrol,_idus)
    datos1=(_idrol,_idus)
    cursor.execute(sql,datos1)
    connection.commit

    flash(" Se agrego con exito") 

    return redirect(url_for('coordinador_integrantes'))


@app.route('/coordinador/integrantes/delete/<string:id>')
def delete(id):

    if not "login" in session:
        return redirect("/")
    
    cursor= connection.cursor()
    sql = "delete from semest where idus={0}".format(id)
    data = (id,)
    cursor.execute(sql, data)
    connection.commit()

    cursor= connection.cursor()
    sql = "delete from intproy where idus={0}".format(id)
    data = (id,)
    cursor.execute(sql, data)
    connection.commit()

    _idrol=4

    cursor=connection.cursor()
    sql="update usuarios set id_rol={0} where idus={1}".format(_idrol,id)
    datos1=(_idrol,id)
    cursor.execute(sql,datos1)
    connection.commit

    flash(" Semillerista eliminado", 'successint') 

    return redirect(url_for('coordinador_integrantes'))


#CRUD Coordinador Evento

@app.route('/coordinador/eventos')
def coordinador_eventos():

    if not "login" in session:
        return redirect("/")

    d = datetime.now()
    dateTask = d.strftime("%Y-%m-%d")

    dateTime=d.strftime("%H:%M")

    cursor=connection.cursor()
    cursor.execute("select * from evento")
    eventos=cursor.fetchall()
    connection.commit()

    return render_template('coordinador/evento.html',fecha_actual=dateTask,hora_actual=dateTime,eventos=eventos)

@app.route('/coordinador/eventos/guardar', methods=['POST'])
def coordinador_eventos_guardar():

    if not "login" in session:
        return redirect("/")

    _nombre=request.form['txtNombre']
    _ubicacion=request.form['txtUbicacion']
    _descripcion=request.form['txtDescripcion']
    _fecha_inicio=request.form['dateInicio']
    _hora=request.form['hora']
    _fecha_fin=request.form['dateFin']

    cursor=connection.cursor()
    sql="insert into evento(nombre, ubicacion, descripcion, fecha_inicio, hora, fecha_fin) values(%s,%s,%s,%s,%s,%s)"
    datos=(_nombre,_ubicacion,_descripcion,_fecha_inicio,_hora,_fecha_fin)
    cursor.execute(sql,datos)
    connection.commit()

    flash(" Evento Creado",'success_evento')
    return redirect(url_for('coordinador_eventos'))

@app.route('/coordinador/eventos/editar/<string:id>', methods=['POST'])
def coordinador_eventos_editar(id):

    if not "login" in session:
        return redirect("/")

    _nombre=request.form['txtNombre']
    _ubicacion=request.form['txtUbicacion']
    _descripcion=request.form['txtDescripcion']
    _fecha_inicio=request.form['dateInicio']
    _hora=request.form['hora']
    _fecha_fin=request.form['dateFin']

    cursor = connection.cursor()
    sql = "UPDATE evento SET nombre = %s, ubicacion = %s, descripcion = %s, fecha_inicio= %s, hora= %s, fecha_fin= %s WHERE codeve = %s"
    datos=(_nombre,_ubicacion,_descripcion,_fecha_inicio,_hora,_fecha_fin,id)
    cursor.execute(sql, datos)
    connection.commit()

    flash(" Evento Actualizado",'success_evento_update')
    return redirect(url_for('coordinador_eventos'))
  

@app.route('/coordinador/eventos/eliminar', methods=['POST'])
def coordinador_eventos_eliminar():

    if not "login" in session:
        return redirect("/")
    
    _id=request.form['codeve']

    cursor=connection.cursor()
    cursor.execute("delete from vincularproy where codeve={0}".format(_id))
    connection.commit()

    cursor=connection.cursor()
    cursor.execute("delete from evento where codeve={0}".format(_id))
    connection.commit()

    flash(" Evento Eliminado ",'success_evento_elim')

    return redirect(url_for('coordinador_eventos'))

@app.route('/coordinador/Coordproyectos/eventos/vincular/<string:id>',methods=['GET','POST'])
def vincular_proyecto(id):

    if not "login" in session:
        return redirect("/")
    
    email=session['email']

    cursor=connection.cursor()
    cursor.execute("select idproy,titulo,tipoproy,estado from proyecto where email='{0}'".format(email))
    proyectos=cursor.fetchall()
    connection.commit()

    cursor=connection.cursor()
    cursor.execute("select vp.idproy,vp.codeve,titulo,tipoproy,estado,nombre from vincularproy as vp inner join proyecto as p on p.idproy=vp.idproy inner join evento as e on e.codeve=vp.codeve where vp.codeve={0}".format(id))
    vinculados=cursor.fetchall()
    connection.commit()

    return render_template('coordinador/vincular.html', proyectos=proyectos, idevento=id, vinculados=vinculados)

@app.route('/coordinador/Coordproyectos/eventos/vincularproy', methods=['GET', 'POST'])
def agregar_proyecto():

    if not "login" in session:
        return redirect("/")

    idproy=request.form['idproy']
    idevento=request.form['idevento']

    cursor=connection.cursor()
    cursor.execute("select * from vincularproy where idproy={0} and codeve={1}".format(idproy,idevento))
    repetido=cursor.fetchall()
    connection.commit()

    if repetido:
        flash(' El proyecto ya esta vinculado', 'errorvincproy')
        return redirect(url_for('vincular_proyecto',id=idevento))
    else:
        cursor=connection.cursor()
        sql="insert into vincularproy (idproy,codeve) values (%s,%s)"
        data=(idproy,idevento)
        cursor.execute(sql, data)
        connection.commit()

        flash(' Proyecto Vinculado', 'proyvinc')
        return redirect(url_for('vincular_proyecto',id=idevento))
    
@app.route('/coordinador/Coordproyectos/eventos/desvincularproy/<string:idproy><string:idevent>')
def desvincular(idproy,idevent):

    if not "login" in session:
        return redirect("/")
    
    email=session['email']
     
    cursor=connection.cursor()
    cursor.execute("select * from proyecto where idproy='{0}' and email='{1}'".format(idproy,email))
    semillero=cursor.fetchall()
    connection.commit()

    if semillero:
        cursor= connection.cursor()
        sql = "delete from vincularproy where idproy={0} and codeve={1}".format(idproy,idevent)
        cursor.execute(sql)
        connection.commit()
        flash(" Proyecto Desvinculado", 'successproydesv') 
    else:
        flash(" Solo el coordinador del semillero puede desvincular este proyecto",'errordenegado')

    return redirect(url_for('vincular_proyecto',id=idevent))

#Funcion Coordinador Crear/Editar proyecto

@app.route('/coordinador/Coordproyectos', methods=['GET', 'POST'])
def semillero_coord():  

    if not "login" in session:
        return redirect("/")

    email=session['email']
    cursor=connection.cursor()
    cursor.execute("select * from semillero where email='{0}'".format(email))
    sem=cursor.fetchall()
    connection.commit()

    idsem=str(sem[0][0])

    if request.method=="POST" and 'buscarproy' in request.form:
        cursor = connection.cursor()
        cursor.execute("select * from proyecto where idsem={0} and titulo like '%".format(idsem) + request.form['buscarproy'] + "%'")
        proyecto=cursor.fetchall()

        if proyecto:
            connection.commit()
        else:
            flash(request.form['buscarproy'],'errorsearch')
    else:
        cursor=connection.cursor()
        cursor.execute("select * from proyecto where idsem='{0}'".format(idsem))
        proyecto=cursor.fetchall()
        connection.commit()

    return render_template('coordinador/Coordproyectos.html',sem=sem,proyecto=proyecto)

@app.route('/new-task', methods=['GET', 'POST'])
def newTask():

    if not "login" in session:
        return redirect("/")
    
    idsem=request.form['idsem']
    email=session['email']
    title = request.form['title']
    description = request.form['description']
    tiproy=request.form['tiproy']
    d = datetime.now()
    dateTask = d.strftime("%Y/%m/%d %H:%M:%S")
    estado=request.form['cmbx_estado']
    
    cursor=connection.cursor()
    sql = "INSERT INTO proyecto (email, titulo, descripcion, fecha, idsem, tipoproy, estado) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    data = (email, title, description, dateTask, idsem, tiproy, estado)
    cursor.execute(sql, data)
    connection.commit()

    flash(" Proyecto creado", 'succesproy')
    
    return redirect(url_for('semillero_coord'))

@app.route('/coordinador/Coordproyectos/proyecto/estado/<string:id>', methods=['POST'])
def coord_estado(id):

    if not "login" in session:
        return redirect("/")

    email=session['email']
    title = request.form['title']
    description = request.form['description']
    d = datetime.now()
    dateTask = d.strftime("%Y/%m/%d %H:%M:%S")
    tiproy=request.form['tiproy']
    estado=request.form['cmbx_estado']

    cursor = connection.cursor()
    cursor.execute("update proyecto set email='{0}',titulo='{1}',descripcion='{2}',fecha='{3}',tipoproy='{4}',estado='{5}' where idproy={6}".format(email,title,description,dateTask,tiproy,estado,id))
    connection.commit()

    return redirect(url_for('semillero_coord'))

#Función Coordinador Agregar/Quitar participante del proyecto

@app.route('/coordinador/Coordproyectos/participante/<string:id>',methods=['GET','POST'])
def participante(id):

    if not "login" in session:
        return redirect("/")

    cursor=connection.cursor()
    cursor.execute("select u.idus,username,email from usuarios as u inner join semest as sm on u.idus=sm.idus")
    semest=cursor.fetchall()
    connection.commit()

    cursor=connection.cursor()
    cursor.execute("select ip.idproy,username,email,ip.idus from intproy as ip inner join usuarios as u on ip.idus=u.idus where idproy={0}".format(id))
    participantes=cursor.fetchall()
    connection.commit()

    return render_template('coordinador/participante.html', semest=semest,idproy=id,participantes=participantes)

@app.route('/coordinador/Coordproyectos/agregarpart', methods=['GET', 'POST'])
def agregar_integrantes():

    if not "login" in session:
        return redirect("/")

    idproy=request.form['idproy']
    idus=request.form['idus']

    cursor=connection.cursor()
    cursor.execute("select count(idproy) from intproy where idproy={0}".format(idproy))
    ints = cursor.fetchall()
    connection.commit()

    cursor=connection.cursor()
    cursor.execute("select * from intproy where idproy={0} and idus={1}".format(idproy,idus))
    repetido=cursor.fetchall()
    connection.commit()

    if repetido:
        flash(' El integrante ya forma parte del proyecto', 'errorintrep')
        return redirect(url_for('participante',id=idproy))
    elif int(ints[0][0])>=5:
        flash(' El proyecto tiene un maximo de 5 integrantes', 'errorints')
        return redirect(url_for('participante',id=idproy))
    else:
        cursor=connection.cursor()
        sql="insert into intproy (idproy,idus) values (%s,%s)"
        data=(idproy,idus)
        cursor.execute(sql, data)
        connection.commit()
        return redirect(url_for('participante',id=idproy))
    
@app.route('/coordinador/Coordproyectos/quitarpart', methods=['GET', 'POST'])
def del_integrantes():

    if not "login" in session:
        return redirect("/")

    idproy=request.form['idproy']
    idus=request.form['idus']

    cursor=connection.cursor()
    cursor.execute(" delete from intproy where idus='{0}' and idproy={1}".format(idus,idproy))
    connection.commit()

    return redirect(url_for('participante',id=idproy))

#Agregar Comentario Coordinador
@app.route('/coordinador/Coordproyectos/proyecto/comentar', methods=['POST'])
def comentario():

    if not "login" in session:
        return redirect("/")
    
    com=request.form['comentario']
    id_ev=request.form['id_ev']
    id_proy=request.form['id_proy']
    
    cursor=connection.cursor()
    cursor.execute("update evidencia set comentario='{0}' where idev={1}".format(com,id_ev))
    connection.commit()

    flash(' Comentario Enviado', 'success_coment')

    return redirect(url_for('proyecto',id=id_proy))

@app.route('/coordinador/Coordproyectos/proyecto/editcoment', methods=['POST'])
def editcoment():
    if not "login" in session:
        return redirect("/")

    com=request.form['comentario']
    id_ev=request.form['id_ev']
    id_proy=request.form['id_proy']

    cursor=connection.cursor()
    cursor.execute("update evidencia set comentario='{0}' where idev={1}".format(com,id_ev))
    connection.commit()

    flash(' Comentario Actualizado', 'success_editcoment')

    return redirect(url_for('proyecto',id=id_proy))


#CRUD Coordinador Evidencia

@app.route('/coordinador/Coordproyectos/proyecto/<string:id>',methods=['GET','POST'])
def proyecto(id):

    if not "login" in session:
        return redirect("/")

    cursor=connection.cursor()
    cursor.execute("select * from proyecto where idproy='{0}'".format(id))
    idev=cursor.fetchall()
    connection.commit()

    cursor=connection.cursor()
    cursor.execute("select * from evidencia where idproy='{0}'".format(id))
    evidencias=cursor.fetchall()
    connection.commit()

    return render_template('coordinador/proyecto.html',idev=idev,evidencias=evidencias)

@app.route('/new-evidencia', methods=['GET', 'POST'])
def crear_evidencia():

    if not "login" in session:
        return redirect("/")
    
    idproy=request.form['idproy_ev']
    titulo=request.form['title_ev']
    descripcion=request.form['desc_ev']

    cursor=connection.cursor()
    sql = "insert into evidencia (idproy, titulo, descripcion) VALUES (%s, %s, %s)"
    data = (idproy,titulo,descripcion)
    cursor.execute(sql, data)
    connection.commit()

    flash(' Evidencia Creada', 'success_ev')

    return redirect(url_for('proyecto',id=idproy))

@app.route('/delete-task', methods=['GET','POST'])
def deleteTask(nombreFoto=''):

    if not "login" in session:
        return redirect("/")

    _id_ev=request.form['id_ev']
    _id_proy=request.form['id_proy']

    cursor =connection.cursor()
    cursor.execute("select archivo from evidencia where idev={0}".format(_id_ev))
    evid = cursor.fetchall()
    connection.commit()

    if os.path.exists("static/archivos/"+str(evid[0][0])):
       os.unlink("static/archivos/"+str(evid[0][0]))

    cursor =connection.cursor()
    cursor.execute("delete from evidencia where idev={0}".format(_id_ev))
    connection.commit()

    flash(' Evidencia Eliminada','elim_ev')

    return redirect(url_for('proyecto',id=_id_proy))

#Funcion Vista Proyecto Semillerista 

@app.route('/semillerista/proyecto', methods=['GET', 'POST'])
def tasks():

    if not "login" in session:
        return redirect("/")

    email=session['email']

    cursor=connection.cursor()
    cursor.execute("select idsem from semest as sm inner join usuarios as us on sm.idus=us.idus where email='{0}'".format(email))
    semi=cursor.fetchall()
    connection.commit()

    cursor = connection.cursor()
    cursor.execute("select distinct on(ip.idproy) ip.idproy,titulo,descripcion,tipoproy,estado from proyecto as p inner join intproy as ip on p.idproy=ip.idproy inner join usuarios as us on us.idus=ip.idus where us.email='{0}'".format(email))
    tasks = cursor.fetchall()
    connection.commit()

    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in tasks:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()

    return render_template('semillerista/proyecto.html', tasks=insertObject,semi=semi)

#Funcion Vista Evidencia Semillerista 

@app.route('/semillerista/proyecto/evidencia/<string:id>',methods=['GET', 'POST'])
def ver_evidencia(id):

    if not "login" in session:
        return redirect("/")

    cursor=connection.cursor()
    cursor.execute("select * from evidencia where idproy='{0}'".format(id))
    evidencias=cursor.fetchall()
    connection.commit()

    return render_template('semillerista/evidencia.html',evidencias=evidencias)


#Función Adjuntar Evidencia Semillerista

@app.route('/semillerista/proyecto/evidencia', methods=['GET','POST'])
def evidencia():

    if not "login" in session:
        return redirect("/")

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
    
    idev=request.form['idev']
    idproy=request.form['idproy']
    archivo=nuevoNombreFile

    cursor=connection.cursor()
    cursor.execute( "update evidencia set archivo='{0}' where idev={1}".format(archivo,idev))
    connection.commit()

    flash(" Evidencia enviada",'editar_ev')

    return redirect(url_for('ver_evidencia',id=idproy, list_Photos = listaArchivos()))


#METODOS DESCARGA DESDE AQUI 

#Funcion que recorre todos los archivos almacenados en la carpeta (archivos)  

def listaArchivos():
    urlFiles = 'static/archivos'
    return (os.listdir(urlFiles))
     
#Creando un Decorador
        
@app.route('/coordinador/Coordproyectos/descargar/<string:nombreFoto>', methods=['GET','POST'])
def descargar_Archivo(nombreFoto=''):
    
    basepath = path.dirname (__file__) 
    url_File = path.join (basepath, 'static/archivos', nombreFoto)

    resp =  send_file(url_File, as_attachment=True)
    return resp

    #send_file toma 2 parametros, el primero será la ruta del archivo y el
    # 2 será as_attachment=True porque deseamos que el archivo sea descargable.
    

#Redireccionando cuando la página no existe
@app.errorhandler(404)
def not_found(error):
    return 'Ruta no encontrada'

#METODOS NUEVO PROYECTO DESDE AQUI

@app.route('/descargarevidencia/<string:id>', methods=['GET','POST'])
def desc_evidencia(idev):

    if not "login" in session:
        return redirect("/")

    cursor=connection.cursor()
    cursor.execute("select archivo from evidencia where idev='{0}'".format(idev))
    archivo=cursor.fetchall()
    connection.commit()

    return render_template(url_for('coordinador/proyecto.html'),archivo=archivo)


@app.route('/coordinador/Coordproyectos/archivos/<ver>')
def archivos(ver):
    print(ver)
    return send_from_directory(os.path.join('static/archivos'),ver)


if __name__=='__main__':
    app.run(debug=True)
