from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Ruta absoluta a la base de datos
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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        conn = get_db_connection()
        existing = conn.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,)).fetchone()
        if existing:
            flash("El usuario ya existe.")
            conn.close()
            return render_template('register.html')

        conn.execute("INSERT INTO usuarios (usuario, contrasena) VALUES (?, ?)", (usuario, contrasena))
        conn.commit()
        conn.close()
        flash("Registro exitoso. Ahora inicia sesión.")
        return redirect(url_for('login'))

    return render_template('register.html')

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

    foto_perfil = user['foto_perfil'] if user['foto_perfil'] else url_for('static', filename='images/perfil_default.jpg')

    return render_template('index2.html',
                           usuario=session['usuario'],
                           usuario_buscado=user['usuario'],
                           nombre=user['nombre'],
                           fecha_nacimiento=user['fecha_nacimiento'],
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

# Ruta para datos_sensor (solo una función, sin duplicados)
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
    return render_template('datos_sensor.html', usuarios=usuarios, user_info=user_info, usuario=session['usuario'])


if __name__ == '__main__':
    print("Arrancando servidor Flask...")
    app.run(debug=True)
