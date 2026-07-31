from flask import current_app


def calcular_precio_unitario(producto, usuario, cantidad_en_carrito_del_producto):
    """Determina el precio unitario y la tarifa aplicada para `producto`
    según el tipo de comprador y la regla de auto-descuento por docena.

    Regla de negocio (REGLA DE NEGOCIO CLAVE del plan): si la cantidad total
    del MISMO producto en el carrito alcanza o supera el umbral configurado
    (12 unidades), el precio se recalcula automáticamente al Precio
    Mayorista / Por Docena, sin importar el tipo de cliente.

    Por debajo del umbral:
      - Cliente B2B (Minorista o Mayorista) autenticado y aprobado: Precio Minorista.
      - Cualquier otro caso (público, no autenticado): Precio Público (menudeo).
    """
    umbral = current_app.config["UMBRAL_PRECIO_DOCENA"]

    if cantidad_en_carrito_del_producto >= umbral:
        return producto.precio_mayorista, "Docena"

    es_b2b_aprobado = (
        usuario is not None
        and usuario.is_authenticated
        and usuario.es_cliente_externo()
        and usuario.nivel_b2b_solicitado in ("Minorista", "Mayorista")
        and usuario.estado_aprobacion_b2b == "Aprobado"
    )
    if es_b2b_aprobado:
        return producto.precio_minorista, "Minorista"

    return producto.precio_publico, "Menudeo"
