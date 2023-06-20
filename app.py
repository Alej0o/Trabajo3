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