import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Define o caminho base do projeto
basedir = os.path.abspath(os.path.dirname(__file__))

# Cria a instância da aplicação Flask
app = Flask(__name__)

# Configurações da aplicação
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'instance', 'receitas.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Cria a pasta 'instance' se ela não existir
instance_path = os.path.join(basedir, 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

# Inicializa a extensão SQLAlchemy
db = SQLAlchemy(app)

# ----------------- MODELOS -----------------
class Chef(db.Model):
    __tablename__ = "chefs"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

    perfil = db.relationship("PerfilChef", back_populates="chef", uselist=False)
    receitas = db.relationship("Receita", back_populates="chef")


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

    ingredientes = db.relationship("ReceitaIngrediente", back_populates="receita")


class Ingrediente(db.Model):
    __tablename__ = "ingredientes"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)

    receitas = db.relationship("ReceitaIngrediente", back_populates="ingrediente")


class ReceitaIngrediente(db.Model):
    __tablename__ = "receitas_ingredientes"
    id = db.Column(db.Integer, primary_key=True)
    quantidade = db.Column(db.String(50))

    receita_id = db.Column(db.Integer, db.ForeignKey("receitas.id"))
    ingrediente_id = db.Column(db.Integer, db.ForeignKey("ingredientes.id"))

    receita = db.relationship("Receita", back_populates="ingredientes")
    ingrediente = db.relationship("Ingrediente", back_populates="receitas")
    
    # ----------------- CLI -----------------
@app.cli.command('init-db')
def init_db_command():
    """Cria as tabelas e popula com dados de exemplo."""
    db.drop_all()
    db.create_all()

    chef1 = Chef(nome='Ana Maria')
    perfil1 = PerfilChef(especialidade='Culinária Brasileira', anos_experiencia=25, chef=chef1)
    chef2 = Chef(nome='Érick Jacquin')
    perfil2 = PerfilChef(especialidade='Culinária Francesa', anos_experiencia=30, chef=chef2)

    db.session.add_all([chef1, chef2, perfil1, perfil2])

    receita1 = Receita(titulo='Molho de Tomate Clássico', instrucoes='...', chef=chef1)
    receita2 = Receita(titulo='Bolo Simples', instrucoes='...', chef=chef1)
    receita3 = Receita(titulo='Petit Gâteau', instrucoes='...', chef=chef2)

    db.session.add_all([receita1, receita2, receita3])
    db.session.commit()

    print('Banco de dados inicializado com sucesso!')


# ----------------- ROTAS -----------------
@app.route('/')
def index():
    receitas = Receita.query.all()
    return render_template('index.html', receitas=receitas)

@app.route('/receita/nova', methods=['GET', 'POST'])
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
        return redirect(url_for('index'))

    chefs = Chef.query.all()
    return render_template('criar_receita.html', chefs=chefs)

@app.route('/chef/novo', methods=['GET', 'POST'])
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

        return redirect(url_for('index'))

    return render_template('criar_chef.html')

@app.route('/chef/<int:chef_id>')
def detalhes_chef(chef_id):
    chef = Chef.query.get_or_404(chef_id)
    return render_template('detalhes_chef.html', chef=chef)

@app.route('/chefs')
def listar_chefs():
    chefs = Chef.query.all()
    return render_template('chefs.html', chefs=chefs)


# ----------------- ERROS -----------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# ----------------- MAIN -----------------
if __name__ == '__main__':
    app.run(debug=True, port=5001)
