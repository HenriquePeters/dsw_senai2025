import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Define o caminho base do projeto
basedir = os.path.abspath(os.path.dirname(__file__))

# Cria a instância da aplicação Flask
app = Flask(__name__)

# Configurações da aplicação
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'instance', 'receitas.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'minha_chave_secreta'  # troque depois para algo seguro

# Cria a pasta 'instance' se ela não existir
instance_path = os.path.join(basedir, 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

# Inicializa a extensão SQLAlchemy
db = SQLAlchemy(app)

# ----------------- MODELOS -----------------
class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.senha_hash, senha)


class Chef(db.Model):
    __tablename__ = "chefs"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

    perfil = db.relationship("PerfilChef", back_populates="chef", uselist=False, cascade="all, delete")
    receitas = db.relationship("Receita", back_populates="chef", cascade="all, delete")


class PerfilChef(db.Model):
    __tablename__ = "perfis_chefs"
    id = db.Column(db.Integer, primary_key=True)
    especialidade = db.Column(db.String(100))
    anos_experiencia = db.Column(db.Integer)

    chef_id = db.Column(db.Integer, db.ForeignKey("chefs.id"))
    chef = db.relationship("Chef", back_populates="perfil")


class Receita(db.Model):
    __tablename__ = "receitas"
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    instrucoes = db.Column(db.Text, nullable=False)

    chef_id = db.Column(db.Integer, db.ForeignKey("chefs.id"), nullable=False)
    chef = db.relationship("Chef", back_populates="receitas")

    ingredientes = db.relationship("ReceitaIngrediente", back_populates="receita", cascade="all, delete")


class Ingrediente(db.Model):
    __tablename__ = "ingredientes"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)

    receitas = db.relationship("ReceitaIngrediente", back_populates="ingrediente", cascade="all, delete")


class ReceitaIngrediente(db.Model):
    __tablename__ = "receitas_ingredientes"
    id = db.Column(db.Integer, primary_key=True)
    quantidade = db.Column(db.String(50))

    receita_id = db.Column(db.Integer, db.ForeignKey("receitas.id"))
    ingrediente_id = db.Column(db.Integer, db.ForeignKey("ingredientes.id"))

    receita = db.relationship("Receita", back_populates="ingredientes")
    ingrediente = db.relationship("Ingrediente", back_populates="receitas")

# ----------------- CLI -----------------
@app.cli.command("init-db")
def init_db_command():
    """Cria as tabelas e popula com dados de exemplo."""
    db.drop_all()
    db.create_all()

    # Usuário admin
    admin = Usuario(usuario="admin")
    admin.set_password("123")
    db.session.add(admin)

    # Criando Chefs
    chef1 = Chef(nome='Ana Maria')
    perfil1 = PerfilChef(especialidade='Culinária Brasileira', anos_experiencia=25, chef=chef1)

    chef2 = Chef(nome='Érick Jacquin')
    perfil2 = PerfilChef(especialidade='Culinária Francesa', anos_experiencia=30, chef=chef2)

    db.session.add_all([chef1, chef2, perfil1, perfil2])

    # Criando Ingredientes
    ingredientes = {
        'tomate': Ingrediente(nome='tomate'),
        'cebola': Ingrediente(nome='cebola'),
        'farinha': Ingrediente(nome='farinha'),
        'ovo': Ingrediente(nome='ovo'),
        'manteiga': Ingrediente(nome='manteiga')
    }

    db.session.add_all(ingredientes.values())

    # Criando Receitas
    receita1 = Receita(titulo='Molho de Tomate Clássico', instrucoes='Corte tomates e cozinhe...', chef=chef1)
    receita2 = Receita(titulo='Bolo Simples', instrucoes='Misture farinha, ovos e manteiga...', chef=chef1)
    receita3 = Receita(titulo='Petit Gâteau', instrucoes='Prepare a massa com chocolate e asse rapidamente...', chef=chef2)

    db.session.add_all([receita1, receita2, receita3])

    # Ligando Ingredientes às Receitas
    db.session.add_all([
        ReceitaIngrediente(receita=receita1, ingrediente=ingredientes['tomate'], quantidade='5 unidades'),
        ReceitaIngrediente(receita=receita1, ingrediente=ingredientes['cebola'], quantidade='1 unidade'),
        ReceitaIngrediente(receita=receita2, ingrediente=ingredientes['farinha'], quantidade='2 xícaras'),
        ReceitaIngrediente(receita=receita2, ingrediente=ingredientes['ovo'], quantidade='3 unidades'),
        ReceitaIngrediente(receita=receita3, ingrediente=ingredientes['manteiga'], quantidade='150g'),
    ])

    db.session.commit()
    print("✅ Banco de dados inicializado com sucesso! Usuário admin criado (admin/123)")

# ----------------- LOGIN/LOGOUT -----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario_nome = request.form['usuario']
        senha = request.form['senha']

        usuario = Usuario.query.filter_by(usuario=usuario_nome).first()

        if usuario and usuario.check_password(senha):
            session['usuario'] = usuario.usuario
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for('index'))
        else:
            flash("Usuário ou senha incorretos!", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash("Você saiu do sistema.", "info")
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuario_nome = request.form['usuario']
        senha = request.form['senha']

        if Usuario.query.filter_by(usuario=usuario_nome).first():
            flash("Usuário já existe!", "warning")
            return redirect(url_for('register'))

        novo_usuario = Usuario(usuario=usuario_nome)
        novo_usuario.set_password(senha)
        db.session.add(novo_usuario)
        db.session.commit()

        flash("Usuário criado com sucesso! Agora faça login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# ----------------- PROTEÇÃO -----------------
def login_required(func):
    def wrapper(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper
