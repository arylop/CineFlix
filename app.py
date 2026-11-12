from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "cambia-esta-clave-en-produccion"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "cineflix.db")


def get_db_connection():
    """Abre una conexión con la base de datos SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crea la tabla si todavía no existe."""
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reservaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            pelicula TEXT NOT NULL,
            fecha TEXT NOT NULL,
            horario TEXT NOT NULL,
            boletos INTEGER NOT NULL,
            sala TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def reserva():
    errores = []
    form_data = {}

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        pelicula = request.form.get("pelicula", "").strip()
        fecha = request.form.get("fecha", "").strip()
        horario = request.form.get("horario", "").strip()
        boletos_txt = request.form.get("boletos", "").strip()
        sala = request.form.get("sala", "").strip()

        form_data = request.form

        peliculas_validas = [
            "Intensamente 2", "Coco", "Elementos", "Robot salvaje"
        ]
        horarios_validos = ["14:00", "17:00", "20:00"]
        salas_validas = ["Tradicional", "VIP", "3D"]

        if not nombre:
            errores.append("El nombre es obligatorio.")

        if pelicula not in peliculas_validas:
            errores.append("Selecciona una película válida.")

        if not fecha:
            errores.append("Selecciona una fecha.")

        if horario not in horarios_validos:
            errores.append("Selecciona un horario válido.")

        if not boletos_txt.isdigit() or not (1 <= int(boletos_txt or 0) <= 10):
            errores.append("La cantidad debe estar entre 1 y 10 boletos.")

        if sala not in salas_validas:
            errores.append("Selecciona un tipo de sala válido.")

        if errores:
            return render_template(
                "reserva.html",
                errores=errores,
                form_data=form_data
            )

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO reservaciones
            (nombre, pelicula, fecha, horario, boletos, sala)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nombre, pelicula, fecha, horario, int(boletos_txt), sala))

        conn.commit()
        conn.close()

        flash("¡Reservación guardada correctamente!", "success")
        return redirect(url_for("reserva"))

    return render_template(
        "reserva.html",
        errores=errores,
        form_data=form_data
    )


@app.route("/reservaciones")
def listado():
    conn = get_db_connection()
    reservaciones = conn.execute("""
        SELECT * FROM reservaciones ORDER BY id DESC
    """).fetchall()
    conn.close()

    return render_template(
        "listado.html",
        reservaciones=reservaciones
    )


@app.route("/cancelar/<int:reserva_id>", methods=["POST"])
def cancelar(reserva_id):
    conn = get_db_connection()
    conn.execute(
        "DELETE FROM reservaciones WHERE id = ?",
        (reserva_id,)
    )
    conn.commit()
    conn.close()

    flash("La reservación fue cancelada.", "info")
    return redirect(url_for("listado"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)