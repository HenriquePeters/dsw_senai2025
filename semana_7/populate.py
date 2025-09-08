from app import app
from models import db

def popular_banco():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("✅ Banco recriado sem dados iniciais.")

if __name__ == "__main__":
    popular_banco()
