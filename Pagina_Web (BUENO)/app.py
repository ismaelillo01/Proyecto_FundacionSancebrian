from flask import Flask, render_template, request, redirect, url_for, session, flash
import oracledb

app = Flask(__name__)
app.secret_key = 'clave_segura'

# Configuración conexión Oracle
DB_USER = "home_assistant"
DB_PASS = "oracle"
DB_DSN = "192.168.0.18:1521/FREEPDB1"

def get_db_connection():
    return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)

@app.route('/')
def home():
    if 'nombre_usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre_usuario FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('index1.html', nombre=session['nombre_usuario'], usuarios=usuarios)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form['nombre_usuario']
        contrasena = request.form.get('contraseña') or request.form.get('contrasena')
        print(f"Datos recibidos - usuario: {nombre}, contraseña: {contrasena}")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT * FROM usuarios
                       WHERE UPPER(TRIM(nombre_usuario)) = UPPER(TRIM(:nombre_usuario)) AND UPPER(TRIM('contraseña')) = UPPER(TRIM(:contrasena))
                       """, {'nombre_usuario': nombre, 'contrasena': contrasena})

        user = cursor.fetchone()
        print(f"Resultado consulta: {user}")

        cursor.close()
        conn.close()

        if user:
            session['nombre_usuario'] = nombre
            return redirect(url_for('home'))
        else:
            flash("Nombre de usuario o contraseña incorrectos.")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('nombre_usuario', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
