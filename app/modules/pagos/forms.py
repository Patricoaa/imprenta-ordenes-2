from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, DateField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional


class PagoForm(FlaskForm):
    orden_id = SelectField("Orden", coerce=int, validators=[DataRequired()])
    monto = DecimalField("Monto", places=2, validators=[DataRequired()])
    fecha = DateField("Fecha", validators=[DataRequired()])
    metodo = StringField("Método", validators=[Optional()])
    submit = SubmitField("Guardar")