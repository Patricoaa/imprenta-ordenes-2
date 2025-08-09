from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, DecimalField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional


class OrdenForm(FlaskForm):
    cliente_id = SelectField("Cliente", coerce=int, validators=[DataRequired()])
    vendedor_id = SelectField("Vendedor", coerce=int, validators=[Optional()])
    usuario_id = SelectField("Usuario", coerce=int, validators=[DataRequired()])
    fecha = DateField("Fecha", validators=[DataRequired()])
    precio_neto = DecimalField("Precio Neto", places=2, validators=[DataRequired()])
    iva = DecimalField("IVA", places=2, validators=[DataRequired()])
    precio_total = DecimalField("Precio Total", places=2, validators=[DataRequired()])
    observaciones = TextAreaField("Observaciones", validators=[Optional()])
    submit = SubmitField("Guardar")