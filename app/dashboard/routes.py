from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from app.dashboard import dashboard_bp
from app.models_all import Pedido, Usuario, Producto, ItemPedido
from app.extensions import db
from app.utilidades import requiere_rol
from datetime import datetime, timedelta
from collections import defaultdict

UMBRAL_STOCK_BAJO = 5
VENTAS_VALIDAS = ("Pagado", "En preparación", "Entregado")


def obtener_rango_fechas(rango, fecha_desde_str=None, fecha_hasta_str=None):
    ahora = datetime.utcnow()
    local_offset = timedelta(hours=-4)
    ahora_local = ahora + local_offset

    if rango == "hoy":
        inicio_local = datetime(ahora_local.year, ahora_local.month, ahora_local.day, 0, 0, 0)
        desde = inicio_local - local_offset
        hasta = ahora
    elif rango == "7d":
        desde = ahora - timedelta(days=7)
        hasta = ahora
    elif rango == "mes":
        inicio_mes_local = datetime(ahora_local.year, ahora_local.month, 1, 0, 0, 0)
        desde = inicio_mes_local - local_offset
        hasta = ahora
    elif rango == "anio":
        inicio_anio_local = datetime(ahora_local.year, 1, 1, 0, 0, 0)
        desde = inicio_anio_local - local_offset
        hasta = ahora
    elif rango == "personalizado":
        if fecha_desde_str:
            try:
                desde_local = datetime.strptime(fecha_desde_str, "%Y-%m-%d")
                desde = desde_local - local_offset
            except ValueError:
                desde = ahora - timedelta(days=30)
        else:
            desde = ahora - timedelta(days=30)

        if fecha_hasta_str:
            try:
                hasta_local = datetime.strptime(fecha_hasta_str, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
                hasta = hasta_local - local_offset
            except ValueError:
                hasta = ahora
        else:
            hasta = ahora
    else:
        desde = ahora - timedelta(days=30)
        hasta = ahora

    return desde, hasta


@dashboard_bp.route("/")
@login_required
@requiere_rol("Gerente", "Administrador", "Empleado")
def index():
    # Solo personal interno puede ver el dashboard.
    contadores = None
    if current_user.rol.es_personal_interno:
        pedidos_pendientes = Pedido.query.filter_by(estado="Pendiente").count()
        b2b_pendientes = Usuario.query.filter_by(estado_aprobacion_b2b="Pendiente").count()
        stock_bajo = (
            Producto.query.filter(Producto.activo.is_(True), Producto.stock <= UMBRAL_STOCK_BAJO).count()
        )
        contadores = {
            "pedidos_pendientes": pedidos_pendientes,
            "b2b_pendientes": b2b_pendientes,
            "stock_bajo": stock_bajo,
        }
    return render_template("dashboard/index.html", contadores=contadores)


@dashboard_bp.route("/api/stats")
@login_required
@requiere_rol("Gerente", "Administrador", "Empleado")
def api_stats():
    rango = request.args.get("rango", "7d")
    fecha_desde_str = request.args.get("fecha_desde")
    fecha_hasta_str = request.args.get("fecha_hasta")

    desde, hasta = obtener_rango_fechas(rango, fecha_desde_str, fecha_hasta_str)
    local_offset = timedelta(hours=-4)

    # Consulta de items de pedidos válidos
    results = (
        db.session.query(ItemPedido, Pedido, Producto)
        .join(Pedido, ItemPedido.pedido_id == Pedido.id)
        .join(Producto, ItemPedido.producto_id == Producto.id)
        .filter(Pedido.estado.in_(VENTAS_VALIDAS))
        .filter(Pedido.fecha_creacion >= desde)
        .filter(Pedido.fecha_creacion <= hasta)
        .all()
    )

    # Alerta de Stock Crítico
    stock_bajo_query = (
        Producto.query.filter(Producto.activo.is_(True), Producto.stock <= UMBRAL_STOCK_BAJO)
        .order_by(Producto.stock.asc())
        .all()
    )
    stock_critico = []
    for p in stock_bajo_query:
        stock_critico.append({
            "id": p.id,
            "sku": p.sku,
            "nombre": p.nombre,
            "stock": p.stock
        })

    # Restricción de rol Empleado
    es_vendedor = current_user.tiene_rol("Empleado") and not current_user.tiene_rol("Gerente", "Administrador")

    # Métricas generales
    pedidos_ids = set()
    unidades_totales = 0

    # Variables financieras (solo Gerente/Admin)
    ventas_totales_bs = 0.0
    inversion_totales_bs = 0.0

    # Agrupaciones
    ventas_por_fecha = defaultdict(lambda: {"pedidos": set(), "unidades": 0, "ingresos_bs": 0.0, "ganancia_bs": 0.0})
    productos_stats = defaultdict(lambda: {"unidades": 0, "ingresos_bs": 0.0, "ganancia_bs": 0.0})
    canales_stats = defaultdict(lambda: {"unidades": 0, "ingresos_bs": 0.0})

    for item, pedido, producto in results:
        pedidos_ids.add(pedido.id)
        unidades_totales += item.cantidad

        # Agrupación por fecha local (Bolivia)
        fecha_local = (pedido.fecha_creacion + local_offset).strftime("%Y-%m-%d")

        ingreso_item = float(item.subtotal)
        cogs_item = (
            float(item.precio_compra_unitario_usd or 0.0)
            * float(pedido.tipo_cambio_aplicado or 1.0)
            * item.cantidad
        )
        ganancia_item = ingreso_item - cogs_item

        ventas_totales_bs += ingreso_item
        inversion_totales_bs += cogs_item

        # Acumulación por fecha
        ventas_por_fecha[fecha_local]["pedidos"].add(pedido.id)
        ventas_por_fecha[fecha_local]["unidades"] += item.cantidad
        ventas_por_fecha[fecha_local]["ingresos_bs"] += ingreso_item
        ventas_por_fecha[fecha_local]["ganancia_bs"] += ganancia_item

        # Acumulación por producto
        productos_stats[producto.nombre]["unidades"] += item.cantidad
        productos_stats[producto.nombre]["ingresos_bs"] += ingreso_item
        productos_stats[producto.nombre]["ganancia_bs"] += ganancia_item

        # Acumulación por nivel de precio (canal)
        canal = item.nivel_precio or "Minorista"
        canales_stats[canal]["unidades"] += item.cantidad
        canales_stats[canal]["ingresos_bs"] += ingreso_item

    pedidos_totales = len(pedidos_ids)

    # Construir lista de evolución ordenada por fecha
    evolucion_temporal = []
    for fecha, data in sorted(ventas_por_fecha.items()):
        item_data = {
            "fecha": fecha,
            "pedidos": len(data["pedidos"]),
            "unidades": data["unidades"]
        }
        if not es_vendedor:
            item_data["ingresos_bs"] = round(data["ingresos_bs"], 2)
            item_data["ganancia_bs"] = round(data["ganancia_bs"], 2)
        evolucion_temporal.append(item_data)

    # Top productos más vendidos
    top_productos = []
    for nombre, data in sorted(productos_stats.items(), key=lambda x: x[1]["unidades"], reverse=True)[:10]:
        item_prod = {
            "nombre": nombre,
            "unidades": data["unidades"]
        }
        if not es_vendedor:
            item_prod["ingresos_bs"] = round(data["ingresos_bs"], 2)
            item_prod["ganancia_bs"] = round(data["ganancia_bs"], 2)
        top_productos.append(item_prod)

    # Desglose por canal
    por_canal = []
    for canal in ["Minorista", "Mayorista", "Franquicia", "Asesora Libre"]:
        data = canales_stats[canal]
        item_canal = {
            "canal": canal,
            "unidades": data["unidades"]
        }
        if not es_vendedor:
            item_canal["ingresos_bs"] = round(data["ingresos_bs"], 2)
        por_canal.append(item_canal)

    # Contadores de pedidos pendientes y atendidos
    pedidos_pendientes_count = Pedido.query.filter_by(estado="Pendiente").count()
    pedidos_atendidos_count = (
        Pedido.query.filter(Pedido.estado.in_(VENTAS_VALIDAS))
        .filter(Pedido.fecha_creacion >= desde)
        .filter(Pedido.fecha_creacion <= hasta)
        .count()
    )

    response_data = {
        "rol": "Empleado" if es_vendedor else "Gerente/Administrador",
        "pedidos_totales": pedidos_totales,
        "unidades_totales": unidades_totales,
        "pedidos_pendientes": pedidos_pendientes_count,
        "pedidos_atendidos": pedidos_atendidos_count,
        "stock_critico": stock_critico,
        "top_productos": top_productos,
        "evolucion_temporal": evolucion_temporal
    }

    if not es_vendedor:
        response_data["finanzas"] = {
            "ventas_totales_bs": round(ventas_totales_bs, 2),
            "inversion_totales_bs": round(inversion_totales_bs, 2),
            "ganancia_neta_bs": round(ventas_totales_bs - inversion_totales_bs, 2),
            "ticket_promedio_bs": (
                round(ventas_totales_bs / pedidos_totales, 2) if pedidos_totales > 0 else 0.0
            )
        }
        response_data["por_canal"] = por_canal

    return jsonify(response_data)
