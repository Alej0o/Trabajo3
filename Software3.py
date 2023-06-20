from flask import render_template, request, redirect, session
import psycopg2
from flask import send_file
import uuid
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
