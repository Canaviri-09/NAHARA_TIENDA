import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()


class Config:
    # Clave secreta para sesiones y protección CSRF de Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "clave-de-respaldo-no-usar-en-produccion")

    # Conexión a la base de datos PostgreSQL (local, Docker o servicio administrado).
    # NUNCA se usa SQLite, ni siquiera en desarrollo, para evitar incompatibilidades
    # de tipos de datos, llaves foráneas y JSON al migrar a la nube.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # evita conexiones muertas si la BD está en la nube
    }

    # Cookies de sesión de Flask-Login endurecidas
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True

    # Carga de archivos (fotos de productos, comprobantes QR)
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "app", "static", "uploads")
    EXTENSIONES_IMAGEN = {"jpg", "jpeg", "png", "webp"}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # Internacionalización: listas configurables, NO hardcodeadas a un único
    # idioma/moneda. El selector regional del header se llena desde aquí.
    IDIOMAS_DISPONIBLES = ["ES", "EN"]
    MONEDAS_DISPONIBLES = ["BOB", "USD"]
    IDIOMA_DEFECTO = os.environ.get("IDIOMA_DEFECTO", "ES")
    MONEDA_DEFECTO = os.environ.get("MONEDA_DEFECTO", "BOB")

    # Regla de negocio: umbral de unidades del mismo producto en el carrito
    # para activar automáticamente el precio Mayorista / Por Docena.
    # Umbral de cantidad del MISMO producto en el carrito para pasar de
    # Precio por Unidad a Precio Mayorista. Aplica a cualquier comprador
    # (público o B2B) por igual.
    UMBRAL_PRECIO_MAYORISTA = 3
