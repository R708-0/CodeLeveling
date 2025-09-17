import sqlite3
from flask import Flask, render_template, session, request, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session

from helpers import login_required

app = Flask(__name__)


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

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
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        # NOTOFICACIONES (MEJORAR) 
        if not username:
            return "DEBES INGRESAR UN USUARIO"
        if not password:
            return "DEBES INGRESAR UNA CONTRASEÑA"
        if confirm != password:
            return "DEBES CONFIRMAR LA CONTRASENA CORRECTAMENTE"
        
        # registrar en la base de datos
        try:
            password_hash = generate_password_hash(password)
            execute_db("INSERT INTO users (name, hash) VALUES (?, ?);", param=(username, password_hash))
        except Exception as e:
            return "El usuario ya existe"

        return redirect("/login")
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()
    
    if request.method == "POST":
        name = request.form.get("username")
        pas = request.form.get("password")
        # validacion de user y pass
        if not name:
            return "Usuario invalido"
        if not pas:
            return "Contasena invalida"
        
        # consultar usuario a la base de datos
        rows = execute_db("SELECT * FROM users WHERE name = ?;", param=(name,), result=True)

        #comprobar que solo exista un usuario y comprobar hash
        if len(rows) != 1:
            return "usuario/contrasena invalidos"
        
        # guardar id del usuario en la sesion
        session['user_id'] = rows[0]["id"]

        return redirect("/")
    
    return render_template("login.html")


@app.route("/")
@login_required
def perfil():
    
    return render_template("perfil.html")

@app.route("/tareas")
def tareas():
    return render_template("tareas.html")

@app.route("/habilidades")
def habilidades():
    skills = get_skills()
    return render_template("habilidades.html", skills=skills)

if __name__ == "__main__":
    app.run(debug=True)
