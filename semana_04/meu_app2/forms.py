from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, TextAreaField, BooleanField,
    SubmitField, SelectField
)
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from wtforms import ValidationError
from datetime import date


# -------- Registro de Usuário --------
class FormularioRegistro(FlaskForm):
    nome = StringField("Nome Completo", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    senha = PasswordField(
        "Senha",
        validators=[DataRequired(), Length(min=8, message="Mínimo de 8 caracteres")]
    )
    confirmar_senha = PasswordField(
        "Confirmar Senha",
        validators=[DataRequired(), EqualTo("senha", message="As senhas devem coincidir")]
    )
    biografia = TextAreaField("Biografia (opcional)")
    aceitar_termos = BooleanField(
        "Aceito os Termos de Serviço",
        validators=[DataRequired(message="Você precisa aceitar os termos")]
    )
    submit = SubmitField("Registrar")


# -------- Cadastro de Evento (ex-Contato) --------
class EventoForm(FlaskForm):
    nome_evento = StringField("Nome do Evento", validators=[DataRequired()])
    data_evento = DateField(
        "Data do Evento",
        format="%Y-%m-%d",
        validators=[DataRequired(message="Informe a data do evento")]
    )
    organizador = StringField("Organizador", validators=[DataRequired()])
    tipo_evento = SelectField(
        "Tipo do Evento",
        choices=[
            ("Palestra", "Palestra"),
            ("Workshop", "Workshop"),
            ("Meetup", "Meetup"),
            ("Outro", "Outro"),
        ],
        validators=[DataRequired()]
    )
    descricao = TextAreaField("Descrição (obrigatória se o tipo for 'Outro')")
    submit = SubmitField("Cadastrar Evento")

    # Não permitir datas passadas
    def validate_data_evento(self, field):
        if field.data < date.today():
            raise ValidationError("A data do evento não pode estar no passado.")

    # Descrição obrigatória quando tipo = Outro
    def validate_descricao(self, field):
        texto = (field.data or "").strip()
        if self.tipo_evento.data == "Outro" and not texto:
            raise ValidationError("Descrição é obrigatória quando o tipo é 'Outro'.")
