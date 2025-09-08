from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Importa modelos de cada pasta
from um_para_um.models import Chef, PerfilChef
from um_para_muitos.models import Receita
from muitos_para_muitos.models import Ingrediente, receita_ingredientes
