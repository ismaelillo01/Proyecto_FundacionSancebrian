from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'usuarios.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    usuarios = conn.execute("SELECT usuario FROM usuarios").fetchall()
    conn.close()

    return render_template('index1.html', usuario=session['usuario'], usuarios=usuarios)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM usuarios WHERE usuario = ? AND contrasena = ?", (usuario, contrasena)).fetchone()
        conn.close()

        if user:
            session['usuario'] = usuario
            return redirect(url_for('home'))
        else:
            flash("Usuario o contraseña incorrectos.")
            return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

@app.route('/perfil/<usuario_buscado>')
def perfil_usuario(usuario_buscado):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
                SELECT usuario, nombre, fecha_nacimiento, direccion, patologias, foto_perfil
                FROM usuarios
                WHERE usuario = ?
                """, (usuario_buscado,))
    user = cur.fetchone()
    conn.close()

    if not user:
        flash("Usuario no encontrado.")
        return redirect(url_for('home'))

    fecha_nac = user['fecha_nacimiento']
    if fecha_nac:
        try:
            fecha_nacimiento_formateada = datetime.strptime(fecha_nac, "%Y-%m-%d").strftime("%d-%m-%Y")
        except ValueError:
            fecha_nacimiento_formateada = fecha_nac
    else:
        fecha_nacimiento_formateada = None

    foto_perfil = user['foto_perfil'] if user['foto_perfil'] else url_for('static', filename='images/perfil_default.jpg')

    return render_template('index2.html',
                           usuario=session['usuario'],
                           usuario_buscado=user['usuario'],
                           nombre=user['nombre'],
                           fecha_nacimiento=fecha_nacimiento_formateada,
                           direccion=user['direccion'],
                           patologias=user['patologias'],
                           foto_perfil=foto_perfil)

@app.route('/buscar_usuario')
def buscar_usuario():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuario_buscado = request.args.get('usuario')
    if not usuario_buscado:
        flash("No se especificó usuario para buscar.")
        return redirect(url_for('home'))

    return redirect(url_for('perfil_usuario', usuario_buscado=usuario_buscado))

@app.route('/datos_sensor', methods=['GET', 'POST'])
def datos_sensor():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    usuarios = conn.execute("SELECT usuario FROM usuarios").fetchall()

    user_info = None
    if request.method == 'POST':
        usuario_buscado = request.form.get('usuario')
        if usuario_buscado:
            user_info = conn.execute("""
                                     SELECT usuario, nombre, fecha_nacimiento, direccion, patologias, foto_perfil
                                     FROM usuarios
                                     WHERE usuario = ?
                                     """, (usuario_buscado,)).fetchone()
            if not user_info:
                flash("Usuario no encontrado.")

    conn.close()

    # Datos sensores - aquí podrás integrar con Home Assistant luego
    sensores = [
        {"nombre": "Sensor temperatura", "estancia": "Cocina", "ultimo_dato": "22°C", "fecha_hora": "2025-05-21 12:15", "bateria": "80%"},
        {"nombre": "Detector de humo", "estancia": "Cocina", "ultimo_dato": "No detectado", "fecha_hora": "2025-05-21 12:00", "bateria": "100%"},
        {"nombre": "Sensor de agua", "estancia": "Baño grande", "ultimo_dato": "Sin agua", "fecha_hora": "2025-05-21 11:50", "bateria": "90%"},
        {"nombre": "Sensor movimiento", "estancia": "Sala de estar", "ultimo_dato": "No detectado", "fecha_hora": "2025-05-21 11:45", "bateria": "85%"},
        {"nombre": "Sensor humedad", "estancia": "Dormitorio", "ultimo_dato": "45%", "fecha_hora": "2025-05-21 12:10", "bateria": "75%"},
    ]

    return render_template('datos_sensor.html', usuarios=usuarios, user_info=user_info, sensores=sensores, usuario=session['usuario'])

if __name__ == '__main__':
    print("Arrancando servidor Flask...")
    app.run(debug=True)
