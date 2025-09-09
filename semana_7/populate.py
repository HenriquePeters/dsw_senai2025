from app import app
from models import db, Chef, PerfilChef, Receita, Ingrediente


def popular_banco():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Criar Chefs
        chef1 = Chef(nome="Gordon Ramsay")
        chef2 = Chef(nome="Massimo Bottura")
        chef3 = Chef(nome="Helena Rizzo")

        db.session.add_all([chef1, chef2, chef3])
        db.session.commit()

        # Perfis (1:1)
        perfil1 = PerfilChef(especialidade="Culinária Britânica", anos_experiencia=30, chef=chef1)
        perfil2 = PerfilChef(especialidade="Culinária Italiana", anos_experiencia=25, chef=chef2)
        perfil3 = PerfilChef(especialidade="Culinária Brasileira", anos_experiencia=20, chef=chef3)

        db.session.add_all([perfil1, perfil2, perfil3])
        db.session.commit()

        # Ingredientes
        farinha = Ingrediente(nome="Farinha")
        ovos = Ingrediente(nome="Ovos")
        acucar = Ingrediente(nome="Açúcar")
        tomate = Ingrediente(nome="Tomate")
        queijo = Ingrediente(nome="Queijo")
        manjericao = Ingrediente(nome="Manjericão")

        db.session.add_all([farinha, ovos, acucar, tomate, queijo, manjericao])
        db.session.commit()

        # Receitas (1:N e M:N)
        receita1 = Receita(
            titulo="Bolo de Açúcar",
            instrucoes="Misture farinha, ovos e açúcar. Leve ao forno por 40 minutos.",
            chef=chef1
        )
        receita1.ingredientes.extend([farinha, ovos, acucar])

        receita2 = Receita(
            titulo="Pizza Margherita",
            instrucoes="Abra a massa, adicione tomate, queijo e manjericão. Asse em forno a lenha.",
            chef=chef2
        )
        receita2.ingredientes.extend([farinha, tomate, queijo, manjericao])

        receita3 = Receita(
            titulo="Moqueca Baiana",
            instrucoes="Cozinhe o peixe com leite de coco, pimentão e coentro.",
            chef=chef3
        )
        # ingredientes simplificados
        receita3.ingredientes.extend([tomate, manjericao])

        db.session.add_all([receita1, receita2, receita3])
        db.session.commit()

        print("✅ Banco populado com sucesso!")

if __name__ == "__main__":
    popular_banco()
