from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Optional


class SMTPForm(FlaskForm):
    host = StringField("SMTP Host", validators=[Optional()])
    port = StringField("SMTP Port", validators=[Optional()])
    username = StringField("SMTP Username", validators=[Optional()])
    password = StringField("SMTP Password", validators=[Optional()])
    use_tls = StringField("SMTP Use TLS (true/false)", validators=[Optional()])
    from_addr = StringField("From", validators=[Optional()])
    submit = SubmitField("Guardar")