from models import db   # <-- usa o db centralizado

class Chef(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

    perfil = db.relationship("PerfilChef", back_populates="chef", uselist=False)

class PerfilChef(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    especialidade = db.Column(db.String(100), nullable=False)
    anos_experiencia = db.Column(db.Integer, nullable=False)

    chef_id = db.Column(db.Integer, db.ForeignKey("chef.id"))
    chef = db.relationship("Chef", back_populates="perfil")
