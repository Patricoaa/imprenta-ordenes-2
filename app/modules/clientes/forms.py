from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Optional, Email


class ClienteForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired()])
    rut = StringField("RUT", validators=[Optional()])
    telefono = StringField("Teléfono", validators=[Optional()])
    correo = StringField("Correo", validators=[Optional(), Email()])
    submit = SubmitField("Guardar")