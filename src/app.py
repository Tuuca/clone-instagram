from flask import Flask, render_template, session, redirect, request, url_for
import mysql.connector

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = 'clone-instagram-secret_key'
app.config['SESSION_TYPE'] = 'filesystem'

usuario = "root" # <------- COLOQUE AQUI O USUÁRIO DO MYSQL ----------------------------#
senha = "fatec" # <------- COLOQUE AQUI A SENHA DO MYSQL ---------------------------#

try:
    mydb = mysql.connector.connect(
    host="localhost",
    user=usuario,
    password=senha
    )
except:
    print("Erro ao conectar ao banco de dados, verifique as credenciais")
    exit()

cur = mydb.cursor()

cur.execute("CREATE DATABASE IF NOT EXISTS CLONE_INSTAGRAM;")
cur.execute("USE CLONE_INSTAGRAM;")

cur.execute("CREATE TABLE IF NOT EXISTS USUARIO (idusuario INT PRIMARY KEY AUTO_INCREMENT NOT NULL, email varchar(100) NOT NULL, nome varchar(100) NOT NULL, senha varchar(100) NOT NULL, foto varchar(100) NOT NULL);")

cur.execute("CREATE TABLE IF NOT EXISTS POST (idpost INT PRIMARY KEY AUTO_INCREMENT NOT NULL, idusuario INT NOT NULL, foto varchar(100) NOT NULL, descricao varchar(100) NOT NULL, FOREIGN KEY (idusuario) REFERENCES USUARIO(idusuario));")

cur.execute("CREATE TABLE IF NOT EXISTS COMENTARIO (idcomentario INT PRIMARY KEY AUTO_INCREMENT NOT NULL, idpost INT NOT NULL, idusuario INT NOT NULL, comentario varchar(100) NOT NULL, FOREIGN KEY (idpost) REFERENCES POST(idpost), FOREIGN KEY (idusuario) REFERENCES USUARIO(idusuario));")

cur.execute("CREATE TABLE IF NOT EXISTS CURTIDA (idcurtida INT PRIMARY KEY AUTO_INCREMENT NOT NULL, idpost INT NOT NULL, idusuario INT NOT NULL, FOREIGN KEY (idpost) REFERENCES POST(idpost), FOREIGN KEY (idusuario) REFERENCES USUARIO(idusuario));")

mydb = mysql.connector.connect(
    host="localhost",
    user=usuario,
    password=senha,
    database="CLONE_INSTAGRAM"
)

cur = mydb.cursor()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return redirect('login')

@app.route('/login', methods=['POST','GET'])
def login():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        if 'senha' not in request.form and 'email' not in request.form:
            msg = 'Preencha todos os campos'
        else:
            cur.execute(f"SELECT * FROM USUARIO WHERE email = '{email}' AND senha = '{senha}'")
            usuario = cur.fetchone()
            if usuario:
                session['loggedin'] = True
                session['idusuario'] = usuario[0]
                session['email'] = usuario[1]
                session['nome'] = usuario[2]
                session['senha'] = usuario[3]
                session['foto'] = usuario[4]
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
        email = request.form['email']
        nome = request.form['nome']
        senha = request.form['senha']
        csenha = request.form['csenha']
        if 'senha' not in request.form and 'csenha' not in request.form and 'nome' not in request.form:
            msg = 'Preencha todos os campos'
        elif senha != csenha:
            msg = 'As senhas não se conferem'
        else:
            cur.execute(f"SELECT * FROM usuario where email = '{email}'")
            usuario = cur.fetchone()
            if usuario:
                msg = 'Usuário já cadastrado'
            else:
                cur.execute(f"INSERT INTO usuario (nome, senha, email, foto) VALUES ('{nome}', '{senha}', '{email}', 'default.png')")
                mydb.commit()
                return redirect(url_for('login'))
        
    return render_template('cadastro.html', msg=msg)

@app.route("/home", methods=['POST', 'GET'])
def home():
    nome = session['nome']
    return render_template('home.html', nome=nome)
    
if __name__ == '__main__':
    app.run(debug=True)