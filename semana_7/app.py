from flask import Flask, render_template, request, redirect, url_for
from models import db, Chef, PerfilChef, Receita, Ingrediente

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///receitas.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    receitas = Receita.query.all()
    return render_template("index.html", receitas=receitas)

@app.route("/receita/nova", methods=["GET", "POST"])
def criar_receita():
    chefs = Chef.query.all()
    if request.method == "POST":
        titulo = request.form["titulo"]
        instrucoes = request.form["instrucoes"]
        chef_id = request.form["chef"]
        ingredientes_texto = request.form["ingredientes"]

        receita = Receita(titulo=titulo, instrucoes=instrucoes, chef_id=chef_id)

        ingredientes_lista = [i.strip() for i in ingredientes_texto.split(",")]
        for nome in ingredientes_lista:
            ingrediente = Ingrediente.query.filter_by(nome=nome).first()
            if not ingrediente:
                ingrediente = Ingrediente(nome=nome)
                db.session.add(ingrediente)
            receita.ingredientes.append(ingrediente)

        db.session.add(receita)
        db.session.commit()
        return redirect(url_for("index"))

    return render_template("criar_receita.html", chefs=chefs)

@app.route("/chef/<int:chef_id>")
def detalhes_chef(chef_id):
    chef = Chef.query.get_or_404(chef_id)
    return render_template("detalhes_chef.html", chef=chef)

@app.route("/ingrediente/<string:nome_ingrediente>")
def buscar_por_ingrediente(nome_ingrediente):
    ingrediente = Ingrediente.query.filter_by(nome=nome_ingrediente).first_or_404()
    return render_template("buscar_ingrediente.html", ingrediente=ingrediente)

if __name__ == "__main__":
    app.run(debug=True)
