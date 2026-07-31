from datetime import datetime
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.pedidos import pedidos_bp
from app.pedidos.utils_notificaciones import notificar_cambio_estado
from app.notas_venta.utils_numeracion import siguiente_numero_nota
from app.extensions import db
from app.models_all import Pedido, ESTADOS_PEDIDO
from app.utilidades import requiere_rol

ROLES_GESTION = ("Gerente", "Administrador", "Empleado")


# ---------------------------------------------------------------------------
# Gestión interna de pedidos (Flujo C de la especificación)
# ---------------------------------------------------------------------------
@pedidos_bp.route("/")
@login_required
@requiere_rol(*ROLES_GESTION)
def listar():
    estado_filtro = request.args.get("estado")
    consulta = Pedido.query
    if estado_filtro:
        consulta = consulta.filter_by(estado=estado_filtro)
    pedidos = consulta.order_by(Pedido.fecha_creacion.desc()).all()
    return render_template("pedidos/listar.html", pedidos=pedidos, estados=ESTADOS_PEDIDO, estado_filtro=estado_filtro)


@pedidos_bp.route("/<int:pedido_id>")
@login_required
@requiere_rol(*ROLES_GESTION)
def detalle(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    return render_template("pedidos/detalle.html", pedido=pedido)


@pedidos_bp.route("/<int:pedido_id>/verificar-pago", methods=["POST"])
@login_required
@requiere_rol(*ROLES_GESTION)
def verificar_pago(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    if pedido.estado != "Pendiente de verificación":
        flash("Este pedido ya fue procesado.", "warning")
        return redirect(url_for("pedidos.detalle", pedido_id=pedido.id))

    pedido.estado = "Pagado"
    pedido.verificado_por_id = current_user.id
    pedido.fecha_verificacion = datetime.utcnow()
    if pedido.numero_nota is None:
        pedido.numero_nota = siguiente_numero_nota()
    db.session.commit()

    notificar_cambio_estado(pedido)
    flash(f"Pago verificado. Nota de Venta N° {pedido.numero_nota} generada.", "success")
    return redirect(url_for("pedidos.detalle", pedido_id=pedido.id))


@pedidos_bp.route("/<int:pedido_id>/rechazar", methods=["POST"])
@login_required
@requiere_rol(*ROLES_GESTION)
def rechazar(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    pedido.estado = "Rechazado"
    db.session.commit()
    notificar_cambio_estado(pedido)
    flash("Pedido rechazado.", "info")
    return redirect(url_for("pedidos.detalle", pedido_id=pedido.id))


@pedidos_bp.route("/<int:pedido_id>/en-preparacion", methods=["POST"])
@login_required
@requiere_rol(*ROLES_GESTION)
def en_preparacion(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    if pedido.estado != "Pagado":
        flash("El pedido debe estar Pagado antes de pasar a preparación.", "warning")
    else:
        pedido.estado = "En preparación"
        db.session.commit()
        notificar_cambio_estado(pedido)
        flash("Pedido marcado En preparación.", "success")
    return redirect(url_for("pedidos.detalle", pedido_id=pedido.id))


@pedidos_bp.route("/<int:pedido_id>/entregado", methods=["POST"])
@login_required
@requiere_rol(*ROLES_GESTION)
def entregado(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    pedido.estado = "Entregado"
    db.session.commit()
    notificar_cambio_estado(pedido)
    flash("Pedido marcado como Entregado.", "success")
    return redirect(url_for("pedidos.detalle", pedido_id=pedido.id))


# ---------------------------------------------------------------------------
# Panel del cliente: "Mis Pedidos"
# ---------------------------------------------------------------------------
@pedidos_bp.route("/mis-pedidos")
@login_required
def mis_pedidos():
    if current_user.rol.es_personal_interno:
        return redirect(url_for("pedidos.listar"))

    pedidos = Pedido.query.filter_by(usuario_id=current_user.id).order_by(Pedido.fecha_creacion.desc()).all()
    return render_template("pedidos/mis_pedidos.html", pedidos=pedidos)
