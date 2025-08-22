from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def perfil():
    
    return render_template("perfil.html")

@app.route("/tareas")
def tareas():
    return render_template("tareas.html")

@app.route("/habilidades")
def habilidades():
    skills = db.execute
    return render_template("habilidades.html")


if __name__ == "__main__":
    app.run(debug=True)
