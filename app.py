import os
import sqlite3
from flask import Flask, abort, redirect, render_template, request, url_for

app = Flask(__name__)

DEFAULT_DB_PATH = os.path.join("data", "incidents.db")
app.config["DATABASE"] = os.environ.get("DATABASE_PATH", DEFAULT_DB_PATH)

PRIORITES = ("Faible", "Moyenne", "Élevée")
STATUTS = ("Nouveau", "En cours", "Résolu")


def get_connection():
    """Ouvre une connexion SQLite vers la base de données configurée."""
    db_path = app.config["DATABASE"]
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crée la table des incidents si elle n'existe pas encore."""
    conn = get_connection()
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titre TEXT NOT NULL,
                description TEXT NOT NULL,
                lieu TEXT NOT NULL,
                priorite TEXT NOT NULL,
                statut TEXT NOT NULL DEFAULT 'Nouveau'
            )
            """
        )
    conn.close()


@app.before_request
def ensure_db_initialized():
    init_db()


@app.route("/")
def index():
    conn = get_connection()
    incidents = conn.execute(
        "SELECT * FROM incidents ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return render_template("index.html", incidents=incidents)


@app.route("/incidents/add", methods=["GET", "POST"])
def add_incident():
    if request.method == "POST":
        titre = request.form.get("titre", "").strip()
        description = request.form.get("description", "").strip()
        lieu = request.form.get("lieu", "").strip()
        priorite = request.form.get("priorite", "").strip()

        if not titre or not description or not lieu or priorite not in PRIORITES:
            erreur = "Veuillez remplir tous les champs et choisir une priorité valide."
            return (
                render_template(
                    "add_incident.html",
                    priorites=PRIORITES,
                    erreur=erreur,
                    form_data=request.form,
                ),
                400,
            )

        conn = get_connection()
        with conn:
            conn.execute(
                """
                INSERT INTO incidents (titre, description, lieu, priorite, statut)
                VALUES (?, ?, ?, ?, 'Nouveau')
                """,
                (titre, description, lieu, priorite),
            )
        conn.close()
        return redirect(url_for("index"))

    return render_template("add_incident.html", priorites=PRIORITES, form_data={})


@app.route("/incidents/<int:incident_id>")
def incident_detail(incident_id):
    conn = get_connection()
    incident = conn.execute(
        "SELECT * FROM incidents WHERE id = ?", (incident_id,)
    ).fetchone()
    conn.close()
    if incident is None:
        abort(404)
    return render_template("incident_detail.html", incident=incident, statuts=STATUTS)


@app.route("/incidents/<int:incident_id>/status", methods=["POST"])
def update_status(incident_id):
    statut = request.form.get("statut", "").strip()
    if statut not in STATUTS:
        abort(400)

    conn = get_connection()
    with conn:
        cursor = conn.execute(
            "UPDATE incidents SET statut = ? WHERE id = ?",
            (statut, incident_id),
        )
    conn.close()
    if cursor.rowcount == 0:
        abort(404)
    return redirect(url_for("incident_detail", incident_id=incident_id))


@app.route("/incidents/<int:incident_id>/delete", methods=["POST"])
def delete_incident(incident_id):
    conn = get_connection()
    with conn:
        cursor = conn.execute(
            "DELETE FROM incidents WHERE id = ?", (incident_id,)
        )
    conn.close()
    if cursor.rowcount == 0:
        abort(404)
    return redirect(url_for("index"))


@app.route("/health")
def health():
    return {"status": "OK"}


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
