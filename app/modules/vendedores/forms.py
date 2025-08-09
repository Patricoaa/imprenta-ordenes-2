from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Optional, Email


class VendedorForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired()])
    rut = StringField("RUT", validators=[Optional()])
    telefono = StringField("Teléfono", validators=[Optional()])
    correo = StringField("Correo", validators=[Optional(), Email()])
    categoria_id = SelectField("Categoría", coerce=int, validators=[Optional()])
    submit = SubmitField("Guardar")