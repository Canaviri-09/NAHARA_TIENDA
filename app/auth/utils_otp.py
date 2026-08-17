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


import os
import smtplib
from email.mime.text import MIMEText

def enviar_correo_otp(correo: str, codigo: str) -> None:
    """Envío del código de verificación por correo usando SMTP para producción,
    con fallback a consola en desarrollo si no hay credenciales configuradas.
    """
    mail_username = os.environ.get("MAIL_USERNAME")
    mail_password = os.environ.get("MAIL_PASSWORD")

    # Registrar en consola siempre (útil para auditoría/dev)
    print(f"[NAHARA][OTP] Código generado para {correo}: {codigo} (válido {MINUTOS_VALIDEZ_OTP} min)")

    if mail_username and mail_password:
        try:
            msg = MIMEText(f"Tu código de verificación de NAHARA es: {codigo}\n\nEste código expira en {MINUTOS_VALIDEZ_OTP} minutos.", "plain", "utf-8")
            msg["Subject"] = "Código de verificación - NAHARA"
            msg["From"] = mail_username
            msg["To"] = correo

            with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
                server.starttls()
                server.login(mail_username, mail_password)
                server.send_message(msg)
            print(f"[NAHARA][SMTP-SUCCESS] Correo enviado exitosamente a {correo}")
        except Exception as e:
            print(f"[NAHARA][SMTP-ERROR] Error al enviar correo por SMTP a {correo}: {e}")
            print(f"[NAHARA][SMTP-FALLBACK] Usando OTP impreso en consola: {codigo}")
    else:
        print("[NAHARA][SMTP-INFO] MAIL_USERNAME o MAIL_PASSWORD no configurados en .env. Correo no enviado por SMTP.")


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
