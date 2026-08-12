from app import create_app
from app.extensions import db, bcrypt
from app.models_all import Rol, Usuario

app = create_app()

ROLES_BASE = [
    ("Gerente", True),
    ("Administrador", True),
    ("Empleado", True),
    ("Cliente Publico", False),
    ("Cliente Minorista", False),
    ("Cliente Mayorista", False),
    ("Cliente Franquicia", False),
    ("Cliente Asesora Libre", False),
]

with app.app_context():
    db.create_all()

    for nombre, es_interno in ROLES_BASE:
        if not Rol.query.filter_by(nombre=nombre).first():
            db.session.add(Rol(nombre=nombre, es_personal_interno=es_interno))
    db.session.commit()
    print("Roles base creados/verificados:", [r.nombre for r in Rol.query.all()])

    rol_gerente = Rol.query.filter_by(nombre="Gerente").first()
    if not Usuario.query.filter_by(correo="admin@nahara.com").first():
        gerente = Usuario(
            nombre="Administrador General",
            correo="admin@nahara.com",
            password=bcrypt.generate_password_hash("nahara123").decode("utf-8"),
            rol_id=rol_gerente.id,
            activo=True,
        )
        db.session.add(gerente)
        db.session.commit()
        print("Usuario Gerente semilla creado: admin@nahara.com / nahara123")
    else:
        print("Usuario Gerente semilla ya existía.")
