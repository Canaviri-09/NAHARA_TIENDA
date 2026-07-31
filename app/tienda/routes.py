import os
import uuid
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_

from app.tienda import tienda_bp
from app.tienda.forms import CheckoutForm
from app.tienda.utils_precios import calcular_precio_unitario
from app.tienda.utils_carrito import (
    agregar_al_carrito, actualizar_cantidad_carrito, eliminar_del_carrito,
    vaciar_carrito, calcular_resumen_carrito,
)
from app.productos.utils_imagenes import extension_permitida
from app.extensions import db
from app.models_all import (
    Producto, ProductoTalla, Categoria, ConfiguracionPagoQR, ConfiguracionEmpresa, Pedido, ItemPedido, TALLAS_CALZADO,
)
from app.utilidades import requiere_rol

ESTADOS_VISIBLES_TIENDA = ("Activo", "En Oferta", "Seccion WOW")


# ---------------------------------------------------------------------------
# Catálogo
# ---------------------------------------------------------------------------
@tienda_bp.route("/")
def catalogo():
    consulta = Producto.query.filter(Producto.estado.in_(ESTADOS_VISIBLES_TIENDA))

    categoria_id = request.args.get("categoria_id", type=int)
    if categoria_id:
        consulta = consulta.filter(Producto.categoria_id == categoria_id)

    disponibilidad = request.args.get("disponibilidad")
    if disponibilidad == "en_existencia":
        consulta = consulta.join(ProductoTalla).filter(ProductoTalla.stock > 0).distinct()
    elif disponibilidad == "agotado":
        ids_con_stock = db.session.query(ProductoTalla.producto_id).filter(ProductoTalla.stock > 0).distinct()
        consulta = consulta.filter(~Producto.id.in_(ids_con_stock))

    tallas_filtro = request.args.getlist("talla", type=int)
    if tallas_filtro:
        ids_con_talla = (
            db.session.query(ProductoTalla.producto_id)
            .filter(ProductoTalla.talla.in_(tallas_filtro), ProductoTalla.stock > 0)
            .distinct()
        )
        consulta = consulta.filter(Producto.id.in_(ids_con_talla))

    orden = request.args.get("orden", "relevancia")
    if orden == "az":
        consulta = consulta.order_by(Producto.nombre.asc())
    elif orden == "za":
        consulta = consulta.order_by(Producto.nombre.desc())
    elif orden == "precio_asc":
        consulta = consulta.order_by(Producto.precio_publico.asc())
    elif orden == "precio_desc":
        consulta = consulta.order_by(Producto.precio_publico.desc())
    elif orden == "fecha":
        consulta = consulta.order_by(Producto.fecha_creacion.desc())
    else:
        consulta = consulta.order_by(Producto.fecha_creacion.desc())

    productos = consulta.all()
    categorias = Categoria.query.filter_by(activo=True).order_by(Categoria.nombre).all()

    return render_template(
        "tienda/catalogo.html",
        productos=productos,
        categorias=categorias,
        tallas_calzado=TALLAS_CALZADO,
        calcular_precio_unitario=calcular_precio_unitario,
    )


@tienda_bp.route("/producto/<int:producto_id>")
def producto_detalle(producto_id):
    producto = Producto.query.filter(
        Producto.id == producto_id, Producto.estado.in_(ESTADOS_VISIBLES_TIENDA)
    ).first_or_404()

    precio_unitario, tipo_tarifa = calcular_precio_unitario(producto, current_user, 0)
    precio_docena, _ = calcular_precio_unitario(producto, current_user, current_app.config["UMBRAL_PRECIO_DOCENA"])

    tallas_disponibles = {t.talla: t.stock for t in producto.tallas if t.stock > 0}

    recomendados = (
        Producto.query.filter(
            Producto.categoria_id == producto.categoria_id,
            Producto.id != producto.id,
            Producto.estado.in_(ESTADOS_VISIBLES_TIENDA),
        ).limit(4).all()
    )

    return render_template(
        "tienda/producto_detalle.html",
        producto=producto,
        precio_unitario=precio_unitario,
        tipo_tarifa=tipo_tarifa,
        precio_docena=precio_docena,
        tallas_disponibles=tallas_disponibles,
        recomendados=recomendados,
        umbral_docena=current_app.config["UMBRAL_PRECIO_DOCENA"],
    )


# ---------------------------------------------------------------------------
# Carrito (mini-cart deslizable)
# ---------------------------------------------------------------------------
@tienda_bp.route("/carrito/agregar", methods=["POST"])
def agregar_carrito():
    producto_id = request.form.get("producto_id", type=int)
    talla = request.form.get("talla", type=int)
    cantidad = request.form.get("cantidad", type=int) or 1

    producto = Producto.query.get_or_404(producto_id)
    talla_registro = ProductoTalla.query.filter_by(producto_id=producto_id, talla=talla).first()

    if talla_registro is None or talla_registro.stock <= 0:
        flash("Esa talla no está disponible en este momento.", "danger")
    else:
        agregar_al_carrito(producto_id, talla, cantidad)
        flash(f"'{producto.nombre}' (talla {talla}) agregado al carrito.", "success")

    return redirect(request.referrer or url_for("tienda.catalogo"))


@tienda_bp.route("/carrito/actualizar", methods=["POST"])
def actualizar_carrito():
    producto_id = request.form.get("producto_id", type=int)
    talla = request.form.get("talla", type=int)
    cantidad = request.form.get("cantidad", type=int) or 0
    actualizar_cantidad_carrito(producto_id, talla, cantidad)
    return redirect(url_for("tienda.ver_carrito"))


@tienda_bp.route("/carrito/eliminar", methods=["POST"])
def eliminar_carrito():
    producto_id = request.form.get("producto_id", type=int)
    talla = request.form.get("talla", type=int)
    eliminar_del_carrito(producto_id, talla)
    flash("Producto eliminado del carrito.", "info")
    return redirect(url_for("tienda.ver_carrito"))


@tienda_bp.route("/carrito")
def ver_carrito():
    lineas, total = calcular_resumen_carrito(current_user)
    return render_template("tienda/carrito.html", lineas=lineas, total=total, umbral_docena=current_app.config["UMBRAL_PRECIO_DOCENA"])


# ---------------------------------------------------------------------------
# Checkout y pago por QR / Transferencia
# ---------------------------------------------------------------------------
@tienda_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    lineas, total = calcular_resumen_carrito(current_user)
    if not lineas:
        flash("Tu carrito está vacío.", "warning")
        return redirect(url_for("tienda.catalogo"))

    formulario = CheckoutForm()
    configuracion_qr = ConfiguracionPagoQR.query.first()

    if formulario.validate_on_submit():
        comprobante = request.files.get("comprobante")
        ruta_comprobante = None

        if comprobante and comprobante.filename:
            if not extension_permitida(comprobante.filename):
                flash("El comprobante debe ser una imagen (jpg, jpeg, png o webp).", "danger")
                return render_template(
                    "tienda/checkout.html", formulario=formulario, lineas=lineas, total=total,
                    configuracion_qr=configuracion_qr,
                )
            carpeta = os.path.join(current_app.config["UPLOAD_FOLDER"], "comprobantes")
            os.makedirs(carpeta, exist_ok=True)
            extension = comprobante.filename.rsplit(".", 1)[1].lower()
            nombre_unico = f"{uuid.uuid4().hex}.{extension}"
            comprobante.save(os.path.join(carpeta, nombre_unico))
            ruta_comprobante = f"uploads/comprobantes/{nombre_unico}"

        # Determina el tipo de tarifa predominante del pedido (la de mayor línea)
        tipo_tarifa_pedido = max(lineas, key=lambda l: l["subtotal"])["tipo_tarifa"] if lineas else "Menudeo"

        pedido = Pedido(
            usuario_id=current_user.id,
            tipo_tarifa=tipo_tarifa_pedido,
            tipo_entrega=formulario.tipo_entrega.data,
            direccion_envio=formulario.direccion_envio.data,
            nota=formulario.nota.data,
            subtotal=total,
            total=total,
            comprobante_pago=ruta_comprobante,
            estado="Pendiente de verificación",
        )
        db.session.add(pedido)
        db.session.flush()

        for linea in lineas:
            db.session.add(ItemPedido(
                pedido_id=pedido.id,
                producto_id=linea["producto"].id,
                nombre_producto=linea["producto"].nombre,
                talla=linea["talla"],
                cantidad=linea["cantidad"],
                precio_unitario=linea["precio_unitario"],
                subtotal=linea["subtotal"],
                tipo_tarifa=linea["tipo_tarifa"],
            ))

        db.session.commit()
        vaciar_carrito()

        flash("¡Pedido registrado! Verificaremos tu pago y te contactaremos.", "success")
        return redirect(url_for("tienda.confirmacion_pedido", pedido_id=pedido.id))

    return render_template(
        "tienda/checkout.html", formulario=formulario, lineas=lineas, total=total, configuracion_qr=configuracion_qr,
    )


@tienda_bp.route("/pedido/<int:pedido_id>/confirmacion")
@login_required
def confirmacion_pedido(pedido_id):
    pedido = Pedido.query.filter_by(id=pedido_id, usuario_id=current_user.id).first_or_404()
    return render_template("tienda/confirmacion.html", pedido=pedido)


# ---------------------------------------------------------------------------
# Configuración del QR institucional (Gerente / Administrador)
# ---------------------------------------------------------------------------
@tienda_bp.route("/configurar-pago-qr", methods=["GET", "POST"])
@login_required
@requiere_rol("Gerente", "Administrador")
def configurar_pago_qr():
    configuracion = ConfiguracionPagoQR.query.first()
    if configuracion is None:
        configuracion = ConfiguracionPagoQR()
        db.session.add(configuracion)
        db.session.commit()

    empresa = ConfiguracionEmpresa.query.first()
    if empresa is None:
        empresa = ConfiguracionEmpresa()
        db.session.add(empresa)
        db.session.commit()

    if request.method == "POST":
        configuracion.nombre_beneficiario = request.form.get("nombre_beneficiario", "").strip()
        configuracion.numero_cuenta = request.form.get("numero_cuenta", "").strip()
        configuracion.banco = request.form.get("banco", "").strip()

        empresa.nombre_comercial = request.form.get("nombre_comercial", "NAHARA").strip() or "NAHARA"
        empresa.direccion = request.form.get("direccion", "").strip()
        empresa.nit = request.form.get("nit", "").strip()
        empresa.celular = request.form.get("celular_empresa", "").strip()
        empresa.ciudad = request.form.get("ciudad_empresa", "").strip()

        archivo_qr = request.files.get("imagen_qr")
        if archivo_qr and archivo_qr.filename:
            if extension_permitida(archivo_qr.filename):
                carpeta = os.path.join(current_app.config["UPLOAD_FOLDER"], "qr")
                os.makedirs(carpeta, exist_ok=True)
                extension = archivo_qr.filename.rsplit(".", 1)[1].lower()
                nombre_unico = f"{uuid.uuid4().hex}.{extension}"
                archivo_qr.save(os.path.join(carpeta, nombre_unico))
                configuracion.ruta_imagen_qr = f"uploads/qr/{nombre_unico}"
            else:
                flash("La imagen del QR debe ser jpg, jpeg, png o webp.", "danger")

        db.session.commit()
        flash("Configuración actualizada.", "success")
        return redirect(url_for("tienda.configurar_pago_qr"))

    return render_template("tienda/configurar_qr.html", configuracion=configuracion, empresa=empresa)
