import sqlite3
from flask import Flask, render_template, session
from flask_session import Session

app = Flask(__name__)


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def get_skills():
    db = sqlite3.connect('leveling.db')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute('SELECT * FROM skills')
    rows = cursor.fetchall()
    db.close()

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

@app.route("/")
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
