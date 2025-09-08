from models import db
from um_para_muitos.models import Receita

receita_ingredientes = db.Table(
    "receita_ingredientes",
    db.Column("receita_id", db.Integer, db.ForeignKey("receita.id"), primary_key=True),
    db.Column("ingrediente_id", db.Integer, db.ForeignKey("ingrediente.id"), primary_key=True)
)

class Ingrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)

    receitas = db.relationship("Receita", secondary=receita_ingredientes, backref="ingredientes")
