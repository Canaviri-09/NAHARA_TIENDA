from flask import session
from app.models_all import Producto
from app.tienda.utils_precios import calcular_precio_unitario


def _clave(producto_id, talla):
    return f"{producto_id}:{talla}"


def obtener_carrito_crudo():
    return session.setdefault("carrito", {})


def agregar_al_carrito(producto_id, talla, cantidad):
    carrito = obtener_carrito_crudo()
    clave = _clave(producto_id, talla)
    carrito[clave] = carrito.get(clave, 0) + cantidad
    session.modified = True


def actualizar_cantidad_carrito(producto_id, talla, cantidad):
    carrito = obtener_carrito_crudo()
    clave = _clave(producto_id, talla)
    if cantidad <= 0:
        carrito.pop(clave, None)
    else:
        carrito[clave] = cantidad
    session.modified = True


def eliminar_del_carrito(producto_id, talla):
    carrito = obtener_carrito_crudo()
    carrito.pop(_clave(producto_id, talla), None)
    session.modified = True


def vaciar_carrito():
    session["carrito"] = {}
    session.modified = True


def calcular_resumen_carrito(usuario):
    """Arma la lista de líneas del carrito con precio dinámico aplicado
    (auto-descuento por docena incluido) y el total general.
    """
    carrito = obtener_carrito_crudo()
    lineas = []
    cantidad_por_producto = {}

    # Primero se suma la cantidad total por producto (todas las tallas)
    # para poder aplicar la regla de docena de forma correcta.
    items_parseados = []
    for clave, cantidad in carrito.items():
        producto_id_str, talla_str = clave.split(":")
        producto_id, talla = int(producto_id_str), int(talla_str)
        items_parseados.append((producto_id, talla, cantidad))
        cantidad_por_producto[producto_id] = cantidad_por_producto.get(producto_id, 0) + cantidad

    total_general = 0
    productos_invalidos = []

    for producto_id, talla, cantidad in items_parseados:
        producto = Producto.query.get(producto_id)
        if producto is None or producto.estado not in ("Activo", "En Oferta", "Seccion WOW"):
            productos_invalidos.append((producto_id, talla))
            continue

        precio_unitario, tipo_tarifa = calcular_precio_unitario(
            producto, usuario, cantidad_por_producto[producto_id]
        )
        subtotal = precio_unitario * cantidad
        total_general += subtotal

        lineas.append({
            "producto": producto,
            "talla": talla,
            "cantidad": cantidad,
            "precio_unitario": precio_unitario,
            "tipo_tarifa": tipo_tarifa,
            "subtotal": subtotal,
        })

    # Limpieza silenciosa de referencias a productos que ya no existen/están inactivos
    if productos_invalidos:
        carrito = obtener_carrito_crudo()
        for producto_id, talla in productos_invalidos:
            carrito.pop(_clave(producto_id, talla), None)
        session.modified = True

    return lineas, total_general


def cantidad_total_items():
    return sum(obtener_carrito_crudo().values())
