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
ALLOWED_EXTENSIONS = {"png","jpg","jpeg","gif"}
def allowed_files(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Subir xp de habilidades 
def up_xp_skill(user_id, skill_id, xp_sum=10):
    skill = execute_db("SELECT level, xp, xp_max FROM users_skills WHERE user_id = ? AND skill_id = ?;", param=(user_id, skill_id), result=True)

    xp = skill[0]["xp"] + xp_sum
    lvl = skill[0]["level"]
    xp_max = skill[0]["xp_max"]
    

    if xp >= xp_max:
        lvl += 1
        xp = xp - xp_max
        xp_max = xp_max + (100 * lvl)

        up_xp_user(user_id,1)

        execute_db("UPDATE users_skills SET level = ?, xp = ?, xp_max = ? WHERE user_id = ? AND skill_id = ?", param=(lvl, xp, xp_max, user_id, skill_id))

    execute_db("UPDATE users_skills SET  xp = ? WHERE user_id = ? AND skill_id = ?;", param=(xp, user_id, skill_id))

def up_xp_user(user_id, p_time=1):  
    user = execute_db("SELECT level, xp, xp_max FROM users WHERE id = ?;", param=(user_id,), result=True)

    xp_sum = p_time * 10
    xp = user[0]["xp"] + xp_sum 
    lvl = user[0]["level"]
    xp_max = user[0]["xp_max"]
    xp_actual = user[0]["xp"]

    if xp >= xp_max:
        lvl += 1
        xp = xp - xp_max
        xp_max = xp_max + (100 * lvl)

        execute_db("UPDATE users SET level = ?, xp = ?, xp_max = ? WHERE id = ?", param=(lvl, xp, xp_max, user_id))


    execute_db("UPDATE users SET xp = ? WHERE id = ?",param=(xp, user_id))  