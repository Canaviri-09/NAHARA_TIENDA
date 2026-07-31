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
    """Envío del código OTP por correo.

    NOTA (pendiente de aprobación): todavía no hay un proveedor SMTP
    configurado ni la dependencia `Flask-Mail` instalada. Mientras tanto,
    en modo desarrollo el código se registra en el log del servidor para
    poder probar el flujo completo. Cuando definas el proveedor de correo
    (SMTP propio, SendGrid, etc.) conectamos el envío real aquí.
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
