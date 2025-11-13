import sqlite3
import os
from flask import Flask, render_template, session, request, redirect, flash, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_session import Session

from helpers import login_required

app = Flask(__name__)

app.secret_key = "admin"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["UPLOAD_FOLDER"] = "static/img"
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
ALLOWED_EXTENSIONS = {"png","jpg","jpeg","gif"}
Session(app)

# verificar extenciones de archivo validos
def allowed_files(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# bases de datos
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

def get_skills():
    
    rows = execute_db('SELECT * FROM skills;', result = True)

    skills = []
    for row in rows:
        percent = int((row["xp"] / row["xp_max"]) * 100)
        skills.append(
            {
            'name': row["name"],
            'level': row["level"],
            'xp': row["xp"],
            'xp_max': row["xp_max"],
            'percent': percent,
            'icon': row["icon"],
            'color': row["color"]
            }
        )
    return skills

#           LOGIN Y REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # declaracion de variables
        photo = request.files["photo"]
        name = request.form.get("name").title()
        username = request.form.get("username").lower()
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        
        # Validar inputs
        if not name:
            flash("Ingrese su nombre completo")
            return render_template("register.html")
        if not username:
            flash("Debes ingresar un nombre usuario")
            return render_template("register.html")
        if not password:
            flash("Debes ingresar una contraseña")
            return render_template("register.html")
        if confirm != password:
            flash("La contraseña y la confirmación no coinciden")
            return render_template("register.html")
        
        # guardar foto en base de datos y validar formato
        photo_filename = None
        if photo :
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            photo_filename = filename
        
            if not allowed_files(photo.filename):
                flash("Formato de imagen no permitido (png, jpg, jpeg, gif)")
                return render_template("register.html")

        # Verificar si el usuario ya existe      
        existing = execute_db("SELECT * FROM users WHERE username = ?", param=(username,), result=True)
        if existing:
            flash("El nombre de usuario ya esta en uso")
            return render_template("register.html")
        
        # registrar en la base de datos
        try:
            password_hash = generate_password_hash(password)
            execute_db("INSERT INTO users (username, hash, name, photo) VALUES (?, ?, ?, ?);", param=(username, password_hash, name, photo_filename))
        except Exception as e:
            flash("Ocurrio un error al registrar :/ intentalo nuevamente")
            return render_template("register.html")

        return redirect("/login")
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if 'user_id' in session:
        return redirect("/")
    
    if request.method == "POST":
        # Declarar variables
        username = request.form.get("username").lower()
        password = request.form.get("password")

        # validacion de user y pass
        if not username:
            flash("Ingrese un usuario válido")
            return render_template("login.html")
        if not password:
            flash("Ingrese una contraseña válida")
            return render_template("login.html")
        
        # consultar usuario a la base de datos
        rows = execute_db("SELECT * FROM users WHERE username = ?;", param=(username,), result=True)
        
        # comprobar que solo exista un usuario y comprobar hash
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Usuario o contraseña inválidos")
            return render_template("login.html")
        
        # guardar id del usuario en la sesion
        session['user_id'] = rows[0]["id"]

        return redirect("/")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/")
@login_required
def perfil():
    skills = get_skills()
    rows = execute_db("SELECT * FROM users WHERE id = ?", param=(session["user_id"],), result=True)
    user = rows[0]
    return render_template("perfil.html", skills=skills, user = user)

@app.route("/tareas")
@login_required
def tareas():
    return render_template("tareas.html")

@app.route("/habilidades")
@login_required
def habilidades():
    return render_template("habilidades.html")

@app.route("/pruebas")
def pruebas():
    return render_template("pruebas.html")

if __name__ == "__main__":
    app.run(debug=True)
