import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Caminho base
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Configurações
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'instance', 'receitas.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'minha_chave_secreta'

# Garante pasta instance
instance_path = os.path.join(basedir, 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

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

# ----------------- ROTAS RECEITAS -----------------
@app.route('/')
@login_required
def index():
    receitas = Receita.query.all()
    return render_template('index.html', receitas=receitas)

@app.route('/receita/nova', methods=['GET', 'POST'])
@login_required
def criar_receita():
    if request.method == 'POST':
        titulo = request.form['titulo']
        instrucoes = request.form['instrucoes']
        chef_id = request.form['chef_id']

        nova_receita = Receita(titulo=titulo, instrucoes=instrucoes, chef_id=chef_id)
        db.session.add(nova_receita)

        ingredientes_str = request.form['ingredientes']
        pares_ingredientes = [par.strip() for par in ingredientes_str.split(',') if par.strip()]

        for par in pares_ingredientes:
            if ':' in par:
                nome, qtd = par.split(':', 1)
                nome_ingrediente = nome.strip().lower()
                quantidade = qtd.strip()

                ingrediente = Ingrediente.query.filter_by(nome=nome_ingrediente).first()
                if not ingrediente:
                    ingrediente = Ingrediente(nome=nome_ingrediente)
                    db.session.add(ingrediente)

                associacao = ReceitaIngrediente(
                    receita=nova_receita,
                    ingrediente=ingrediente,
                    quantidade=quantidade
                )
                db.session.add(associacao)

        db.session.commit()
        flash("Receita criada com sucesso!", "success")
        return redirect(url_for('index'))

    chefs = Chef.query.all()
    return render_template('criar_receita.html', chefs=chefs)

@app.route('/receita/editar/<int:receita_id>', methods=['GET', 'POST'])
@login_required
def editar_receita(receita_id):
    receita = Receita.query.get_or_404(receita_id)
    if request.method == 'POST':
        receita.titulo = request.form['titulo']
        receita.instrucoes = request.form['instrucoes']
        db.session.commit()
        flash("Receita atualizada com sucesso!", "success")
        return redirect(url_for('index'))
    return render_template('editar_receita.html', receita=receita)

@app.route('/receita/excluir/<int:receita_id>', methods=['POST'])
@login_required
def excluir_receita(receita_id):
    receita = Receita.query.get_or_404(receita_id)
    db.session.delete(receita)
    db.session.commit()
    flash("Receita excluída com sucesso!", "danger")
    return redirect(url_for('index'))

# ----------------- ROTAS CHEFS -----------------
@app.route('/chefs')
@login_required
def listar_chefs():
    chefs = Chef.query.all()
    return render_template('chefs.html', chefs=chefs)

@app.route('/chef/novo', methods=['GET', 'POST'])
@login_required
def criar_chef():
    if request.method == 'POST':
        nome = request.form['nome']
        especialidade = request.form['especialidade']
        anos_experiencia = request.form['anos_experiencia']

        novo_chef = Chef(nome=nome)
        db.session.add(novo_chef)
        db.session.commit()

        perfil = PerfilChef(
            especialidade=especialidade,
            anos_experiencia=anos_experiencia,
            chef=novo_chef
        )
        db.session.add(perfil)
        db.session.commit()

        flash("Chef cadastrado com sucesso!", "success")
        return redirect(url_for('listar_chefs'))

    return render_template('criar_chef.html')

@app.route('/chef/editar/<int:chef_id>', methods=['GET', 'POST'])
@login_required
def editar_chef(chef_id):
    chef = Chef.query.get_or_404(chef_id)
    if request.method == 'POST':
        chef.nome = request.form['nome']
        chef.perfil.especialidade = request.form['especialidade']
        chef.perfil.anos_experiencia = request.form['anos_experiencia']
        db.session.commit()
        flash("Chef atualizado com sucesso!", "success")
        return redirect(url_for('listar_chefs'))
    return render_template('editar_chef.html', chef=chef)

@app.route('/chef/excluir/<int:chef_id>', methods=['POST'])
@login_required
def excluir_chef(chef_id):
    chef = Chef.query.get_or_404(chef_id)
    db.session.delete(chef)
    db.session.commit()
    flash("Chef excluído com sucesso!", "danger")
    return redirect(url_for('listar_chefs'))

@app.route('/chef/<int:chef_id>')
@login_required
def detalhes_chef(chef_id):
    chef = Chef.query.get_or_404(chef_id)
    return render_template('detalhes_chef.html', chef=chef)

# ----------------- ERROS -----------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# ----------------- MAIN -----------------
if __name__ == '__main__':
    app.run(debug=True, port=5001)
