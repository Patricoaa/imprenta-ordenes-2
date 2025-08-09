from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Optional, Length


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Ingresar")


class UsuarioForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=255)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    rol = SelectField("Rol", choices=[("admin", "Admin"), ("staff", "Staff"), ("vendedor", "Vendedor")])
    password = PasswordField("Password", validators=[Optional()])
    submit = SubmitField("Guardar")