from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional


class LoginStaffForm(FlaskForm):
    """Login del personal interno: correo + contraseña."""
    correo = StringField("Correo", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    submit = SubmitField("Ingresar")


class SolicitarOTPForm(FlaskForm):
    """Paso 1 del login de clientes externos: pide el correo para
    enviarle un código OTP de 6 dígitos."""
    correo = StringField("Correo", validators=[DataRequired(), Email()])
    submit = SubmitField("Enviar código")


class VerificarOTPForm(FlaskForm):
    """Paso 2 del login de clientes externos: valida el código recibido."""
    correo = StringField("Correo", validators=[DataRequired(), Email()])
    codigo = StringField("Código de verificación", validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField("Verificar")


class RegistroClienteForm(FlaskForm):
    """Registro de clientes externos: Público, Minorista o Mayorista.
    Los campos B2B (NIT/CI, razón social) solo son obligatorios para
    Minorista/Mayorista; la validación cruzada se hace en la ruta.
    """
    nombre = StringField("Nombre completo", validators=[DataRequired(), Length(max=150)])
    correo = StringField("Correo", validators=[DataRequired(), Email()])
    telefono = StringField("Celular", validators=[DataRequired(), Length(max=30)])
    ciudad = StringField("Ciudad", validators=[Optional(), Length(max=100)])

    tipo_cliente = SelectField(
        "Tipo de cliente",
        choices=[
            ("Publico", "Público (menudeo)"),
            ("Minorista", "Minorista (B2B - cuarta docena)"),
            ("Mayorista", "Mayorista (B2B - por docena)"),
        ],
        validators=[DataRequired()],
    )

    nit_ci = StringField("NIT / CI", validators=[Optional(), Length(max=30)])
    razon_social = StringField("Razón social", validators=[Optional(), Length(max=150)])

    submit = SubmitField("Registrarme")
