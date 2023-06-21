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