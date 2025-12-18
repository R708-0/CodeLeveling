import sqlite3
from flask import redirect, render_template, session
from functools import wraps
from werkzeug.utils import secure_filename

# VALIDAR INICIO DE SESION
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") ==  None:
            return redirect("/login")
        return f(*args, **kwargs)
    
    return decorated_function

# EJECUTAR QUERY EN BASE DE DATOS
def execute_db(query, param=(),result = False):
    connection = sqlite3.connect('leveling.db')
    connection.row_factory = sqlite3.Row
    db = connection.cursor()
    db.execute(query,param)

    rows = None
    if result == True:
        rows = db.fetchall() 

    connection.commit()
    connection.close()

    return rows

# VERIFICAR EXTENSIONES DE ARCHIVOS VALIDOS
def allowed_files(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS