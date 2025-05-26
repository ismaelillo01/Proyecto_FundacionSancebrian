from flask import Flask, render_template, request, session, redirect, url_for, flash
import oracledb

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

def get_db_connection():
    try:
        conn = oracledb.connect(
            user="home_assistant",
            password="oracle",
            dsn="192.168.0.54:1521/FREEPDB1"
        )
        return conn
    except Exception as e:
        print("Error DB:", e)
        return None

@app.route('/', methods=['GET'])
def home():
    if 'nombre_usuario' not in session:
        return redirect(url_for('login'))

    usuario_buscado = request.args.get('usuario', None)

    conn = get_db_connection()
    if conn is None:
        flash("Error al conectar a la base de datos.")
        return redirect(url_for('login'))

    cur = conn.cursor()
    # Obtener todos los usuarios para el datalist
    cur.execute("SELECT nombre_usuario FROM usuarios")
    usuarios = [{'nombre_usuario': row[0]} for row in cur.fetchall()]

    user_detail = None
    if usuario_buscado:
        cur.execute("""
                    SELECT nombre_usuario, fecha_nacimiento, direccion, patologias
                    FROM usuarios WHERE nombre_usuario = :usuario_buscado
                    """, usuario_buscado=usuario_buscado)
        row = cur.fetchone()
        if row:
            user_detail = {
                'nombre_usuario': row[0],
                'fecha_nacimiento': row[1],
                'direccion': row[2],
                'patologias': row[3],
            }
        else:
            flash("Usuario no encontrado.")

    cur.close()
    conn.close()

    return render_template('index.html', nombre=session.get('nombre_usuario'),
                           usuarios=usuarios,
                           user_detail=user_detail)

@app.route('/mostrar_usuario')
def mostrar_usuario():
    # Puedes dejar esta ruta o eliminarla si ya no la usas
    return redirect(url_for('home'))

@app.route('/datos_sensor', methods=['GET', 'POST'])
def datos_sensor():
    if 'nombre_usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn is None:
        flash("Error al conectar a la base de datos.")
        return redirect(url_for('home'))

    cur = conn.cursor()
    cur.execute("SELECT nombre_usuario FROM usuarios")
    usuarios = [{'usuario': row[0]} for row in cur.fetchall()]

    user_info = None
    sensores = []

    if request.method == 'POST':
        usuario_sel = request.form.get('usuario')
        cur.execute("""
                    SELECT nombre_usuario, fecha_nacimiento, direccion, patologias
                    FROM usuarios WHERE nombre_usuario = :usuario_sel
                    """, usuario_sel=usuario_sel)
        user_data = cur.fetchone()

        if user_data:
            user_info = {
                'nombre': user_data[0],
                'fecha_nacimiento': user_data[1],
                'direccion': user_data[2],
                'patologias': user_data[3],
                'foto_perfil': url_for('static', filename='img/img_1.png')  # fija o dinámica según tu lógica
            }
            cur.execute("""
                        SELECT nombre, estancia, ultimo_dato, fecha_hora, bateria FROM sensores
                        WHERE usuario = :usuario_sel
                        ORDER BY fecha_hora DESC
                            FETCH FIRST 10 ROWS ONLY
                        """, usuario_sel=usuario_sel)
            sensores = [
                {'nombre': r[0], 'estancia': r[1], 'ultimo_dato': r[2], 'fecha_hora': r[3], 'bateria': r[4]}
                for r in cur.fetchall()
            ]
    cur.close()
    conn.close()

    return render_template('datos_sensor.html', nombre=session.get('nombre_usuario'), usuarios=usuarios, user_info=user_info, sensores=sensores)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        contraseña = request.form.get('password')  # nombre del campo en formulario, puede ser 'password' o 'contraseña'
        conn = get_db_connection()
        if conn is None:
            flash("Error al conectar a la base de datos.")
            return render_template('login.html')

        cur = conn.cursor()
        cur.execute("""
                    SELECT nombre_usuario FROM usuarios
                    WHERE nombre_usuario = :usuario AND contraseña = :contraseña
                    """, usuario=usuario, contraseña=contraseña)
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session['nombre_usuario'] = user[0]
            return redirect(url_for('home'))
        else:
            flash("Usuario o contraseña incorrectos.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
