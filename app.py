import os
from flask import Flask, render_template, session, request, redirect, flash, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session

from helpers import login_required
from helpers import execute_db, up_xp_skill, up_xp_user

app = Flask(__name__)

app.secret_key = "admin"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["UPLOAD_FOLDER"] = "static/img"
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
ALLOWED_EXTENSIONS = {"png","jpg","jpeg","gif"}
Session(app)


#           LOGIN Y REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # declaracion de variables
        photo = request.files["photo"]
        name = request.form.get("name").title()
        description = request.form.get("description")
        username = request.form.get("username").lower()
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        
        # Validar inputs
        if not name:
            flash("Ingrese su nombre completo", "danger")
            return render_template("register.html")
        if not username:
            flash("Debes ingresar un nombre usuario", "danger")
            return render_template("register.html")
        if not password:
            flash("Debes ingresar una contraseña", "danger")
            return render_template("register.html")
        if confirm != password:
            flash("La contraseña y la confirmación no coinciden", "danger")
            return render_template("register.html")
        # Descripcion es opcional
        
        # guardar foto en base de datos y validar formato
        photo_filename = None
        if photo :
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            photo_filename = filename
        
            if not allowed_files(photo.filename):
                flash("Formato de imagen no permitido (png, jpg, jpeg, gif)", "danger")
                return render_template("register.html")

        # Verificar si el usuario ya existe      
        existing = execute_db("SELECT * FROM users WHERE username = ?", param=(username,), result=True)
        if existing:
            flash("El nombre de usuario ya esta en uso", "danger")
            return render_template("register.html")
        
        # registrar en la base de datos
        try:
            password_hash = generate_password_hash(password)
            execute_db("INSERT INTO users (username, hash, name, photo, description) VALUES (?, ?, ?, ?, ?);", param=(username, password_hash, name, photo_filename, description))
        except Exception as e:
            flash("Ocurrio un error al registrar :/ intentalo nuevamente", "danger")
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
            flash("Ingrese un usuario válido", "danger")
            return render_template("login.html")
        if not password:
            flash("Ingrese una contraseña válida", "danger")
            return render_template("login.html")
        
        # consultar usuario a la base de datos
        rows = execute_db("SELECT * FROM users WHERE username = ?;", param=(username,), result=True)
        
        # comprobar que solo exista un usuario y comprobar hash
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Usuario o contraseña inválidos", "danger")
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
    # Variables 
    skills = execute_db("SELECT s.icon, s.name, us.level FROM users_skills us JOIN skills s ON us.skill_id = s.id WHERE us.user_id = ?",param=(session["user_id"],),result=True)
    projects = execute_db("""SELECT id, name, link FROM projects WHERE user_id = ? 
    AND id IN (SELECT ref_id FROM completed_tasks WHERE user_id = ? AND type = 'project') """, param=(session["user_id"], session["user_id"]),result=True)
    rows = execute_db("SELECT * FROM users WHERE id = ?;", param=(session["user_id"],), result=True)
    user = rows[0]

    # Funcion para el titulo del usuario
    titulo = ""
    if user["level"] <= 30:
        titulo = "Estudiante"
    elif user["level"] <= 60:
        titulo = "Junior"
    elif user["level"] <= 90:
        titulo ="Profesional"
    elif user["level"] <= 100:
        titulo = "Senior"
    else :
        titulo = "Master"

    # Funcion para el rango
    rango = ""
    r = user["level"] % 30
    #print(r)

    if user["level"] >= 100:
        rango ="Leyenda"
    elif user["level"] >= 90:
        rango = "Élite"
    elif user["level"] == 0:
        rango = "Aspirante"
    elif r >= 20 :
        rango = "Élite"
    elif r >= 10 :
        rango = "Avanzado"
    else : 
        rango = "Novato"

    # Renderizar pagina    
    return render_template("perfil.html", skills=skills, user = user, titulo=titulo, rango =rango, projects=projects)

# Eliminar proyectos
@app.route("/eliminar_proyecto", methods=["POST"])
@login_required
def eliminar_proyecto():
    project_id = request.form.get("project_id")
  
    execute_db("DELETE FROM projects WHERE id = ? AND user_id = ?", param=(project_id, session["user_id"]))

    return redirect("/")


# RUTA PRINCIPAL DE TAREAS 
@app.route("/tareas")
@login_required
def tareas():
    skills = execute_db("""SELECT s.id, s.name, s.icon FROM users_skills us
     JOIN skills s ON us.skill_id = s.id WHERE us.user_id = ?
     AND us.skill_id NOT IN (SELECT ref_id FROM completed_tasks 
     WHERE user_id = ? AND type = 'skill');""", param=(session["user_id"], session["user_id"]), result=True)

    projects = execute_db("""SELECT id, name FROM projects WHERE user_id = ?
    AND id NOT IN (SELECT ref_id FROM completed_tasks
    WHERE user_id = ? AND type = 'project');""", param=(session["user_id"], session["user_id"]), result=True)
    
    return render_template("tareas.html", skills=skills, projects=projects)

# Completar tareas
@app.route("/tareas/completar/skill", methods=["POST"])
@login_required
def completar_habilidad():
    ref_id = request.form.get("ref_id")
    execute_db("INSERT INTO completed_tasks (user_id, ref_id, type) Values (?, ?, 'skill')", param=(session["user_id"], ref_id))

    up_xp_skill(session["user_id"], ref_id, 10)

    return redirect("/tareas")

# Completar proyecto
@app.route("/tareas/completar/project", methods=["POST"])
@login_required
def completar_proyecto():
    ref_id = request.form.get("ref_id")
    row = execute_db("SELECT time FROM projects WHERE user_id = ? AND id = ?", param=(session["user_id"], ref_id), result=True)
    p_time = row[0]["time"]    

    execute_db("INSERT INTO completed_tasks (user_id, ref_id, type) VALUES (?, ? , 'project')", param=(session["user_id"],ref_id))

    up_xp_user(session["user_id"], p_time)

    return redirect("/tareas")

# Reiniciar tareas 
@app.route("/tareas/reiniciar", methods=["POST"])
@login_required
def reiniciar():
    execute_db("DELETE FROM completed_tasks WHERE  user_id = ? AND type = 'skill';", param=(session["user_id"],))
    return redirect("/tareas")


# RUTA PRINCIPAL DE HABILIDADES 
@app.route("/habilidades")
@login_required
def habilidades():
    skill_cat = execute_db("SELECT * FROM skills;",result=True)
    skills = execute_db("SELECT s.name, s.icon, us.level, us.xp, us.xp_max FROM users_skills us JOIN skills s ON us.skill_id = s.id WHERE us.user_id = ?", param=(session["user_id"],),result=True)
    return render_template("habilidades.html", skills=skills, skill_cat=skill_cat)

# Aprender habilidades
@app.route("/habilidades/aprender", methods=["POST"])
@login_required
def aprender_habilidad():
    # Validar input de habilidad
    skill_id = request.form.get("skill_id")

    if not skill_id:
        flash("Primero selecciona una habilidad", "danger")
        return redirect("/habilidades")

    # Validar habilidad duplicada
    duplicado = execute_db("SELECT 1 FROM users_skills WHERE user_id = ? AND skill_id = ?", param=(session["user_id"], skill_id), result=True)
    if duplicado:
        flash("Ya aprendiste esa habilidad", "danger")
        return redirect("/habilidades")

    # Actualizar base de datos
    try:
        execute_db("INSERT INTO users_skills (user_id, skill_id) VALUES (?, ?);", param=(session["user_id"], skill_id))
    except Exception as e:
        flash("Ocurrió un error al aprender habilidad :( intente de nuevo)", "danger")
        return redirect("/habilidades")
    return redirect("/habilidades")

# Guardar proyecto
@app.route("/habilidades/proyectos", methods=["POST"])
@login_required
def guardar_proyecto():
    p_name = request.form.get("pj_name")
    p_link = request.form.get("pj_link")
    p_time = request.form.get("pj_time")
   
    # Validacion de inputs
    if not p_name:
        flash("Ingresa un nombre de proyecto", "danger")
        return redirect("/habilidades")
    if not p_link:
        flash("Ingresa un enlace del proyecto", "danger")
        return redirect("/habilidades")
    
    # Validar nombre repetido
    name = execute_db("SELECT 1 FROM projects WHERE user_id = ? AND name = ?", param=(session["user_id"], p_name), result=True)
    if name:
        flash("El nombre de proyecto ya existe", "danger")
        return redirect("/habilidades")

    # Actualizar base de datos
    try:
        execute_db("INSERT INTO projects(name, link, user_id, time) VALUES (?, ?, ?,?);", param=(p_name, p_link, session["user_id"],p_time))
        flash("El proyecto se guardó con éxito","success")
    except Exception as error:
        flash("Ocurrió un error al guardar el proyecto", "danger")
        return redirect("/habilidades")
    return redirect("/habilidades")


if __name__ == "__main__":
    app.run(debug=True)
