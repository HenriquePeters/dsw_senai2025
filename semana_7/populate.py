
from app import app
from models import db, Chef, PerfilChef, Receita, Ingrediente

def popular_banco():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Ingredientes
        farinha = Ingrediente(nome="Farinha")
        ovos = Ingrediente(nome="Ovos")
        acucar = Ingrediente(nome="Açúcar")
        tomate = Ingrediente(nome="Tomate")
        queijo = Ingrediente(nome="Queijo")
        manjericao = Ingrediente(nome="Manjericão")

        db.session.add_all([farinha, ovos, acucar, tomate, queijo, manjericao])
        db.session.commit()

        print("✅ Banco populado com sucesso (apenas ingredientes)!")

if __name__ == "__main__":
    popular_banco()