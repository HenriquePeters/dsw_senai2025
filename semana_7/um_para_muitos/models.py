from models import db
from um_para_um.models import Chef

class Receita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    instrucoes = db.Column(db.Text, nullable=False)

    chef_id = db.Column(db.Integer, db.ForeignKey("chef.id"))
    chef = db.relationship("Chef", backref="receitas")
