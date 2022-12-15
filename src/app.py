from flask import Flask, render_template, session, redirect, request, url_for
from werkzeug.utils import secure_filename
import os
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
    print("Erro ao conectar ao banco de dados, verifique as credenciais ou se o banco de dados está rodando.")
    exit()

cur = mydb.cursor()

cur.execute("CREATE DATABASE IF NOT EXISTS CLONE_INSTAGRAM;")
cur.execute("USE CLONE_INSTAGRAM;")

cur.execute("CREATE TABLE IF NOT EXISTS USUARIO (idusuario INT PRIMARY KEY AUTO_INCREMENT NOT NULL, email varchar(100) NOT NULL, nome varchar(100) NOT NULL, senha varchar(100) NOT NULL, foto varchar(100) NOT NULL, bio varchar(200) NOT NULL);")

cur.execute("CREATE TABLE IF NOT EXISTS POST (idpost INT PRIMARY KEY AUTO_INCREMENT NOT NULL, idusuario INT NOT NULL, foto varchar(100) NOT NULL, descricao varchar(100) NOT NULL, FOREIGN KEY (idusuario) REFERENCES USUARIO(idusuario));")

cur.execute("CREATE TABLE IF NOT EXISTS COMENTARIO (idcomentario INT PRIMARY KEY AUTO_INCREMENT NOT NULL, idpost INT NOT NULL, idusuario INT NOT NULL, comentario varchar(100) NOT NULL, FOREIGN KEY (idpost) REFERENCES POST(idpost), FOREIGN KEY (idusuario) REFERENCES USUARIO(idusuario));")

cur.execute("CREATE TABLE IF NOT EXISTS CURTIDA (idcurtida INT PRIMARY KEY AUTO_INCREMENT NOT NULL, idpost INT NOT NULL, idusuario INT NOT NULL, FOREIGN KEY (idpost) REFERENCES POST(idpost), FOREIGN KEY (idusuario) REFERENCES USUARIO(idusuario));")

cur.execute ("CREATE TABLE IF NOT EXISTS SEGUIDOR (idseguidor INT PRIMARY KEY AUTO_INCREMENT NOT NULL, idusuario INT NOT NULL, idseguido INT NOT NULL, FOREIGN KEY (idusuario) REFERENCES USUARIO(idusuario), FOREIGN KEY (idseguido) REFERENCES USUARIO(idusuario));")

mydb.commit()

# BASE DE DADOS PARA TESTE

cur.execute("SELECT * FROM USUARIO")

if cur.fetchone() == None:

    # DUAS INSERÇÕES DE USUÁRIO E POST APENAS DE TESTE / EXEMPLO

    cur.execute("INSERT INTO USUARIO VALUES (0, 'capirava@gmail.com ', 'Capiravildo', '123', 'perfil1.jpg', 'moro no parque da cidade');")
    cur.execute("INSERT INTO USUARIO VALUES (0, 'gato@gmail.com ', 'Gatodinho', '123', 'perfil2.jpg', 'sou muito maluco');")

    cur.execute("INSERT INTO POST VALUES (0, 1, 'post1.jpg', 'OIA EU DE BATMAN');")
    cur.execute("INSERT INTO POST VALUES (0, 2, 'post2.jpg', 'é o pulas');")

    mydb.commit()

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
    if 'email' in session:
        return redirect('home')
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
    session.pop('email', None)
    session.pop('nome', None)
    session.pop('senha', None)
    session.pop('foto', None)
    return redirect(url_for('login'))

@app.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
    if 'email' in session:
        return redirect('home')
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
                cur.execute(f"INSERT INTO usuario (nome, senha, email, foto, bio) VALUES ('{nome}', '{senha}', '{email}', 'default.png', 'Olá!')")
                mydb.commit()
                return redirect(url_for('login'))
        
    return render_template('cadastro.html', msg=msg)

@app.route("/home", methods=['POST', 'GET'])
def home():
    if not session.get('loggedin'):
        return redirect(url_for('login'))  
    nome = session['nome']
    cur.execute(f"SELECT p.idpost, p.foto, p.descricao , u.nome, u.foto, u.idusuario FROM post p INNER JOIN usuario u ON p.idusuario = u.idusuario ORDER BY p.idpost DESC")
    posts = cur.fetchall()
    print(posts)
    mydb.commit()
    return render_template('home.html', nome=nome, posts=posts, foto=session['foto'], idusuario=session['idusuario'])

@app.route("/publicar", methods=['POST', 'GET'])
def publicar():
    msg = ''
    if not session.get('loggedin'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        descricao = request.form['descricao']
        print(request.files['foto'])
        if 'foto' not in request.files:
            msg = 'Selecione uma foto'
        else:
            foto = request.files['foto']
            if foto.filename == '':
                msg = 'Selecione uma foto'
            elif not allowed_file(foto.filename):
                msg = 'Formato de arquivo não permitido'
            elif foto:
                cur.execute(f"INSERT INTO post (idusuario, foto, descricao) VALUES ({session['idusuario']}, '', '{descricao}')")
                mydb.commit()
                cur.execute("SELECT MAX(idpost) FROM post")
                idImagem = cur.fetchone()[0]
                filename = secure_filename(f"post{idImagem}.{foto.filename.rsplit('.', 1)[1].lower()}")
                foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cur.execute(f"UPDATE post SET foto = '{filename}' WHERE idpost = {idImagem}")
                mydb.commit()
                return redirect(url_for('home'))
    return render_template('publicar.html', foto=session['foto'], msg=msg)

@app.route("/perfil/<idusuario>")
def perfil(idusuario):
    if not session.get('loggedin'):
        return redirect(url_for('login'))
    cur.execute(f"SELECT nome, foto, bio FROM usuario WHERE idusuario = {idusuario}")
    usuario = cur.fetchone()
    cur.execute(f"SELECT idpost, foto FROM post WHERE idusuario = {idusuario}")
    posts = cur.fetchall()
    mydb.commit()
    return render_template('perfil.html', usuario=usuario, posts=posts, foto=session['foto'])
    
@app.route("/editarPerfil", methods=['POST', 'GET'])
def editarPerfil():
    if not session.get('loggedin'):
        return redirect(url_for('login'))
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
            cur.execute(f"UPDATE usuario SET nome = '{nome}', senha = '{senha}' WHERE idusuario = {session['idusuario']}")
            mydb.commit()
            return redirect(url_for('home'))
    return render_template('editarPerfil.html', foto=session['foto'], msg=msg)

if __name__ == '__main__':
    app.run(debug=True)