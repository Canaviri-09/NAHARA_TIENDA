from flask import render_template
from flask_login import login_required, current_user
from app.dashboard import dashboard_bp
from app.extensions import db
from app.models_all import Pedido, Usuario, ProductoTalla, Producto

UMBRAL_STOCK_BAJO = 5


@dashboard_bp.route("/")
@login_required
def index():
    contadores = None
    if current_user.rol.es_personal_interno:
        pedidos_pendientes = Pedido.query.filter_by(estado="Pendiente de verificación").count()
        b2b_pendientes = Usuario.query.filter_by(estado_aprobacion_b2b="Pendiente").count()
        stock_bajo = (
            db.session.query(Producto.id)
            .join(ProductoTalla)
            .filter(Producto.estado == "Activo")
            .group_by(Producto.id)
            .having(db.func.sum(ProductoTalla.stock) <= UMBRAL_STOCK_BAJO)
            .count()
        )
        contadores = {
            "pedidos_pendientes": pedidos_pendientes,
            "b2b_pendientes": b2b_pendientes,
            "stock_bajo": stock_bajo,
        }
    return render_template("dashboard/index.html", contadores=contadores)
