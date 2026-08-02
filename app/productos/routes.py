from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.productos import productos_bp
from app.productos.forms import ProductoForm
from app.productos.utils_imagenes import guardar_imagenes_producto, eliminar_imagen_producto
from app.productos.utils_mas_vendidos import obtener_ids_mas_vendidos
from app.extensions import db
from app.models_all import Producto, ProductoImagen, Categoria, Subcategoria
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


@productos_bp.route("/")
@login_required
@requiere_rol(*ROLES_GESTION)
def listar():
    productos = Producto.query.order_by(Producto.fecha_creacion.desc()).all()
    ids_mas_vendidos = obtener_ids_mas_vendidos()
    return render_template("productos/listar.html", productos=productos, ids_mas_vendidos=ids_mas_vendidos)


@productos_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
@requiere_rol(*ROLES_GESTION)
def nuevo():
    formulario = ProductoForm()
    _cargar_choices(formulario, request.form.get("categoria_id", type=int))

    if formulario.validate_on_submit():
        if Producto.query.filter_by(sku=formulario.sku.data.strip()).first():
            flash("Ya existe un producto con ese SKU.", "danger")
            return render_template("productos/formulario.html", formulario=formulario, modo="nuevo")

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
            stock=formulario.stock.data,
            activo=formulario.activo.data,
            es_destacado=formulario.es_destacado.data,
            en_oferta=formulario.en_oferta.data,
            porcentaje_descuento=formulario.porcentaje_descuento.data if formulario.en_oferta.data else None,
            creado_por_id=current_user.id,
        )
        db.session.add(producto)
        db.session.commit()

        archivos = request.files.getlist("fotos")
        guardar_imagenes_producto(producto, archivos)

        flash(f"Producto '{producto.nombre}' creado correctamente.", "success")
        return redirect(url_for("productos.editar", producto_id=producto.id))

    return render_template("productos/formulario.html", formulario=formulario, modo="nuevo")


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
            producto.stock = formulario.stock.data
            producto.activo = formulario.activo.data
            producto.es_destacado = formulario.es_destacado.data
            producto.en_oferta = formulario.en_oferta.data
            producto.porcentaje_descuento = formulario.porcentaje_descuento.data if formulario.en_oferta.data else None

            db.session.commit()

            archivos = request.files.getlist("fotos")
            guardar_imagenes_producto(producto, archivos)

            flash(f"Producto '{producto.nombre}' actualizado correctamente.", "success")
            return redirect(url_for("productos.editar", producto_id=producto.id))

    return render_template("productos/formulario.html", formulario=formulario, modo="editar", producto=producto)


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


# ---------------------------------------------------------------------------
# Promociones masivas: seleccionar varios productos y aplicar/quitar un
# descuento porcentual a todos a la vez (a los 3 niveles de precio).
# ---------------------------------------------------------------------------
@productos_bp.route("/promociones", methods=["GET", "POST"])
@login_required
@requiere_rol(*ROLES_GESTION)
def promociones():
    if request.method == "POST":
        ids_seleccionados = request.form.getlist("producto_id", type=int)
        accion = request.form.get("accion")

        if not ids_seleccionados:
            flash("Selecciona al menos un producto.", "warning")
            return redirect(url_for("productos.promociones"))

        if accion == "aplicar":
            porcentaje = request.form.get("porcentaje", type=float)
            if not porcentaje or porcentaje <= 0 or porcentaje > 95:
                flash("Ingresa un porcentaje de descuento válido (1-95).", "danger")
                return redirect(url_for("productos.promociones"))

            Producto.query.filter(Producto.id.in_(ids_seleccionados)).update(
                {"en_oferta": True, "porcentaje_descuento": porcentaje}, synchronize_session=False
            )
            db.session.commit()
            flash(f"Descuento de {porcentaje:.0f}% aplicado a {len(ids_seleccionados)} producto(s).", "success")

        elif accion == "quitar":
            Producto.query.filter(Producto.id.in_(ids_seleccionados)).update(
                {"en_oferta": False, "porcentaje_descuento": None}, synchronize_session=False
            )
            db.session.commit()
            flash(f"Oferta retirada de {len(ids_seleccionados)} producto(s).", "info")

        return redirect(url_for("productos.promociones"))

    productos = Producto.query.order_by(Producto.en_oferta.desc(), Producto.nombre).all()
    return render_template("productos/promociones.html", productos=productos)
