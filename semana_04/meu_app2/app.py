import os
from flask import Flask, render_template, flash, redirect, url_for
from forms import FormularioRegistro, EventoForm

app = Flask(__name__)
# chave fixa para dev (troque em produção)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")


# ---------- Rotas ----------
@app.route("/")
def index():
    return render_template("index.html")


# Registro de usuário (exercício anterior)
@app.route("/registro", methods=["GET", "POST"])
def registro():
    form = FormularioRegistro()
    if form.validate_on_submit():
        nome = form.nome.data
        bio = form.biografia.data or ""
        msg = f"Bem-vindo, {nome}!"
        if bio.strip():
            msg += f" Sua biografia: {bio[:80]}..."
        flash(msg, "success")
        return redirect(url_for("registro"))
    return render_template("registro.html", form=form)


# Cadastro de Evento (transformado do 'contato')
@app.route("/vazio", methods=["GET", "POST"])
def formulario_vazio():
    form = EventoForm()
    if form.validate_on_submit():
        flash(
            f"Evento '{form.nome_evento.data}' cadastrado para {form.data_evento.data}!",
            "success"
        )
        return redirect(url_for("formulario_vazio"))
    return render_template("formulario.html", form=form, title="Cadastro de Evento")


if __name__ == "__main__":
    # Rode direto com: python app.py
    app.run(debug=True)
