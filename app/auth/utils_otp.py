import random
from datetime import datetime, timedelta

from app.extensions import db
from app.models_all import TokenOTP

MINUTOS_VALIDEZ_OTP = 10


def generar_codigo_otp(correo: str) -> str:
    """Crea un código OTP de 6 dígitos para `correo`, invalida cualquier
    código anterior sin usar de ese correo y lo guarda en la base de datos.
    """
    TokenOTP.query.filter_by(correo=correo, usado=False).update({"usado": True})

    codigo = f"{random.randint(0, 999999):06d}"
    token = TokenOTP(
        correo=correo,
        codigo=codigo,
        expira_en=datetime.utcnow() + timedelta(minutes=MINUTOS_VALIDEZ_OTP),
        usado=False,
    )
    db.session.add(token)
    db.session.commit()
    return codigo


def enviar_correo_otp(correo: str, codigo: str) -> None:
    """Envío del código de verificación por correo.

    Esta función es el ÚNICO lugar del proyecto que envía códigos por
    correo: la usan tanto el login OTP de clientes (app/auth/routes.py)
    como la recuperación de contraseña del personal interno. Conectar el
    envío real aquí basta para que ambos flujos funcionen de una vez.

    ============================================================
    PENDIENTE DE APROBACIÓN (no instalé nada todavía, según tu regla de
    no agregar dependencias sin consultarte primero). Opciones para
    conectar el envío real usando Gmail / Google Workspace:

    OPCIÓN A — SMTP de Gmail con "Contraseña de aplicación" (la más simple):
      1. En la cuenta de Gmail/Google Workspace que enviará los correos:
         activar verificación en 2 pasos y generar una "Contraseña de
         aplicación" en https://myaccount.google.com/apppasswords
      2. Guardar en .env: MAIL_USERNAME (el correo de Gmail) y
         MAIL_PASSWORD (la contraseña de aplicación, NO la contraseña
         normal de la cuenta).
      3. Herramienta: la librería estándar `smtplib` de Python (no
         requiere instalar nada) o, más cómodo, `Flask-Mail` (si me
         apruebas instalarla). Con smtplib el envío sería:

           import smtplib
           from email.mime.text import MIMEText
           msg = MIMEText(f"Tu código NAHARA es: {codigo}")
           msg["Subject"] = "Código de verificación NAHARA"
           msg["From"] = MAIL_USERNAME
           msg["To"] = correo
           with smtplib.SMTP("smtp.gmail.com", 587) as server:
               server.starttls()
               server.login(MAIL_USERNAME, MAIL_PASSWORD)
               server.send_message(msg)

    OPCIÓN B — Gmail API con OAuth2 (más robusta, más pasos):
      Requiere crear un proyecto en Google Cloud Console, habilitar la
      Gmail API, generar credenciales OAuth2, e instalar
      `google-api-python-client` + `google-auth-oauthlib`. Recomendable
      solo si más adelante necesitas enviar muchos correos o adjuntos
      grandes; para códigos OTP la Opción A es suficiente.

    Mientras no se conecte ninguna opción, en modo desarrollo el código
    se registra en el log del servidor para poder probar el flujo
    completo sin depender de un correo real.
    ============================================================
    """
    print(f"[NAHARA][OTP-DEV] Código para {correo}: {codigo} (válido {MINUTOS_VALIDEZ_OTP} min)")


def validar_codigo_otp(correo: str, codigo: str) -> bool:
    """Verifica que el código sea el último emitido para ese correo, no
    esté usado y no haya expirado. Si es válido, lo marca como usado.
    """
    token = (
        TokenOTP.query.filter_by(correo=correo, codigo=codigo, usado=False)
        .order_by(TokenOTP.fecha_creacion.desc())
        .first()
    )
    if token is None:
        return False
    if token.expira_en < datetime.utcnow():
        return False

    token.usado = True
    db.session.commit()
    return True
