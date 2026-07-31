from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.productos import productos_bp
from app.productos.forms import ProductoForm
from app.productos.utils_imagenes import guardar_imagenes_producto, eliminar_imagen_producto
from app.extensions import db
from app.models_all import Producto, ProductoTalla, ProductoImagen, Categoria, Subcategoria, TALLAS_CALZADO
from app.utilidades import requiere_rol

ROLES_GESTION = ("Gerente", "Administrador", "Empleado")


def _cargar_choices(formulario, categoria_id_actual=None):
    formulario.categoria_id.choices = [(c.id, c.nombre) for c in Categoria.query.order_by(Categoria.nombre).all()]
    subcats = Subcategoria.query
    if categoria_id_actual:
        subcats = subcats.filter_by(categoria_id=categoria_id_actual)
    formulario.subcategoria_id.choices = [(0, "— Sin subcategoría —")] + [
        (s.id, s.nombre) for s in subcats.order_by(Subcategoria.nombre).all()
    ]


def _leer_tallas_del_formulario():
    """Lee del request los pares talla/stock enviados por el formulario
    dinámico de la matriz de inventario y devuelve {talla: stock}."""
    tallas = {}
    for talla in TALLAS_CALZADO:
        valor = request.form.get(f"stock_talla_{talla}", "").strip()
        if valor:
            try:
                cantidad = int(valor)
            except ValueError:
                cantidad = 0
            if cantidad > 0:
                tallas[talla] = cantidad
    return tallas


@productos_bp.route("/")
@login_required
@requiere_rol(*ROLES_GESTION)
def listar():
    productos = Producto.query.order_by(Producto.fecha_creacion.desc()).all()
    return render_template("productos/listar.html", productos=productos)


@productos_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
@requiere_rol(*ROLES_GESTION)
def nuevo():
    formulario = ProductoForm()
    _cargar_choices(formulario, request.form.get("categoria_id", type=int))

    if formulario.validate_on_submit():
        if Producto.query.filter_by(sku=formulario.sku.data.strip()).first():
            flash("Ya existe un producto con ese SKU.", "danger")
            return render_template("productos/formulario.html", formulario=formulario, modo="nuevo", tallas_calzado=TALLAS_CALZADO)

        tallas = _leer_tallas_del_formulario()
        subcategoria_id = formulario.subcategoria_id.data or None

        producto = Producto(
            nombre=formulario.nombre.data.strip(),
            sku=formulario.sku.data.strip(),
            descripcion=formulario.descripcion.data,
            categoria_id=formulario.categoria_id.data,
            subcategoria_id=subcategoria_id,
            precio_publico=formulario.precio_publico.data,
            precio_minorista=formulario.precio_minorista.data,
            precio_mayorista=formulario.precio_mayorista.data,
            estado=formulario.estado.data,
            creado_por_id=current_user.id,
        )
        db.session.add(producto)
        db.session.flush()  # asigna producto.id sin cerrar la transacción

        for talla, stock in tallas.items():
            db.session.add(ProductoTalla(producto_id=producto.id, talla=talla, stock=stock))

        db.session.commit()

        archivos = request.files.getlist("fotos")
        guardar_imagenes_producto(producto, archivos)

        flash(f"Producto '{producto.nombre}' creado correctamente.", "success")
        return redirect(url_for("productos.editar", producto_id=producto.id))

    return render_template("productos/formulario.html", formulario=formulario, modo="nuevo", tallas_calzado=TALLAS_CALZADO)


@productos_bp.route("/<int:producto_id>/editar", methods=["GET", "POST"])
@login_required
@requiere_rol(*ROLES_GESTION)
def editar(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    formulario = ProductoForm(obj=producto)
    if request.method == "GET":
        formulario.subcategoria_id.data = producto.subcategoria_id or 0

    _cargar_choices(formulario, request.form.get("categoria_id", type=int) or producto.categoria_id)

    if formulario.validate_on_submit():
        existente = Producto.query.filter_by(sku=formulario.sku.data.strip()).first()
        if existente and existente.id != producto.id:
            flash("Ese SKU ya está en uso por otro producto.", "danger")
        else:
            producto.nombre = formulario.nombre.data.strip()
            producto.sku = formulario.sku.data.strip()
            producto.descripcion = formulario.descripcion.data
            producto.categoria_id = formulario.categoria_id.data
            producto.subcategoria_id = formulario.subcategoria_id.data or None
            producto.precio_publico = formulario.precio_publico.data
            producto.precio_minorista = formulario.precio_minorista.data
            producto.precio_mayorista = formulario.precio_mayorista.data
            producto.estado = formulario.estado.data

            tallas_nuevas = _leer_tallas_del_formulario()
            ProductoTalla.query.filter_by(producto_id=producto.id).delete()
            for talla, stock in tallas_nuevas.items():
                db.session.add(ProductoTalla(producto_id=producto.id, talla=talla, stock=stock))

            db.session.commit()

            archivos = request.files.getlist("fotos")
            guardar_imagenes_producto(producto, archivos)

            flash(f"Producto '{producto.nombre}' actualizado correctamente.", "success")
            return redirect(url_for("productos.editar", producto_id=producto.id))

    stock_por_talla = {t.talla: t.stock for t in producto.tallas}
    return render_template(
        "productos/formulario.html",
        formulario=formulario,
        modo="editar",
        producto=producto,
        tallas_calzado=TALLAS_CALZADO,
        stock_por_talla=stock_por_talla,
    )


@productos_bp.route("/<int:producto_id>/imagenes/<int:imagen_id>/eliminar", methods=["POST"])
@login_required
@requiere_rol(*ROLES_GESTION)
def eliminar_imagen(producto_id, imagen_id):
    imagen = ProductoImagen.query.filter_by(id=imagen_id, producto_id=producto_id).first_or_404()
    eliminar_imagen_producto(imagen)
    flash("Fotografía eliminada.", "info")
    return redirect(url_for("productos.editar", producto_id=producto_id))


@productos_bp.route("/<int:producto_id>/imagenes/<int:imagen_id>/marcar-principal", methods=["POST"])
@login_required
@requiere_rol(*ROLES_GESTION)
def marcar_principal(producto_id, imagen_id):
    ProductoImagen.query.filter_by(producto_id=producto_id).update({"es_principal": False})
    imagen = ProductoImagen.query.filter_by(id=imagen_id, producto_id=producto_id).first_or_404()
    imagen.es_principal = True
    db.session.commit()
    flash("Foto principal actualizada.", "success")
    return redirect(url_for("productos.editar", producto_id=producto_id))
