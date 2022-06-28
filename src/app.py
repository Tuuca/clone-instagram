from flask import Flask, render_template, session, redirect, request
from flask_mysqldb import MySQL

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'

app.config['MYSQL_PASSWORD'] = 'senha' # <- Coloque aqui sua senha do MySQL

app.config['MYSQL_DB'] = 'clone-instagram'
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
        msg = 'Back end ainda não feito :('

    return render_template('login.html', msg=msg)

@app.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
    msg = ''
    if request.method == 'POST':
        msg = 'Back end ainda não feito :('
    return render_template('cadastro.html', msg=msg)