from flask import current_app


def calcular_precio_unitario(producto, usuario, cantidad_en_carrito_del_producto):
    """Determina el precio unitario y la tarifa aplicada para `producto`
    según la CANTIDAD del mismo producto en el carrito — aplica por igual
    a cualquier comprador (público o B2B, sin importar si tiene cuenta
    aprobada):

      - 1 a 2 unidades:   Precio Público (Menudeo)
      - 3 a 11 unidades:  Precio Minorista
      - 12+ unidades:     Precio Mayorista / Por Docena

    `usuario` ya no participa en el cálculo — se mantiene como parámetro
    para no romper las llamadas existentes, por si más adelante se vuelve
    a necesitar un descuento específico por tipo de cuenta.
    """
    umbral_docena = current_app.config["UMBRAL_PRECIO_DOCENA"]
    umbral_minorista = current_app.config["UMBRAL_PRECIO_MINORISTA"]

    if cantidad_en_carrito_del_producto >= umbral_docena:
        return producto.precio_mayorista_final, "Docena"

    if cantidad_en_carrito_del_producto >= umbral_minorista:
        return producto.precio_minorista_final, "Minorista"

    return producto.precio_publico_final, "Menudeo"
