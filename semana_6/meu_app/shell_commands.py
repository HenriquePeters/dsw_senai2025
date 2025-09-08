from app import db, User, Post
db.create_all()

p1 = Post(titulo="Primeiro Post", conteudo="Esse é o conteúdo do meu primeiro post.")
p2 = Post(titulo="Segundo Post", conteudo="Mais um post de exemplo.")

db.session.add_all([p1, p2])
db.session.commit()

Post.query.all()
