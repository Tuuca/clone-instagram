from flask import Flask, render_template, session, redirect, request, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'

app.config['MYSQL_PASSWORD'] = 'tuca123' # <- Coloque aqui sua senha do MySQL

app.config['MYSQL_DB'] = 'instagram'
app.secret_key = 'clone-instagram-secret_key'
app.config['SESSION_TYPE'] = 'filesystem'

mysql = MySQL(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return redirect('login')

@app.route('/login', methods=['POST','GET'])
def login():
    msg = ''
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        if 'senha' not in request.form and 'nome' not in request.form:
            msg = 'Preencha todos os campos'
        else:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM USUARIO WHERE nome = %s AND senha = %s", (nome, senha))
            usuario = cur.fetchone()
            if usuario:
                session['loggedin'] = True
                session['idusuario'] = usuario[0]
                session['nome'] = usuario[1]
                session['senha'] = usuario[2]
                return redirect(url_for('home'))
            else:
                msg = 'Usuário ou senha incorretos!'

    return render_template('login.html', msg=msg)

@app.route("/logout")
def logout():
    session.pop('loggedin', None)
    session.pop('idusuario', None)
    session.pop('nome', None)
    session.pop('senha', None)
    return redirect(url_for('login'))

@app.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
    msg = ''
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        csenha = request.form['csenha']
        if 'senha' not in request.form and 'csenha' not in request.form and 'nome' not in request.form:
            msg = 'Preencha todos os campos'
        elif senha != csenha:
            msg = 'As senhas não se conferem'
        else:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM usuario where nome = %s", (nome,))
            usuario = cur.fetchone()
            if usuario:
                msg = 'Usuário já cadastrado'
            else:
                cur.execute("INSERT INTO USUARIO (nome, senha) VALUES (%s, %s)", (nome, senha))
                cur.connection.commit()
                cur.close()
                return redirect(url_for('login'))
        
    return render_template('cadastro.html', msg=msg)

@app.route("/home", methods=['POST', 'GET'])
def home():
    nome = session['nome']
    return render_template('home.html', nome=nome)