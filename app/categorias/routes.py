from flask import render_template, redirect, url_for, flash
from flask_login import login_required

from app.categorias import categorias_bp
from app.categorias.forms import CategoriaForm, SubcategoriaForm
from app.extensions import db
from app.models_all import Categoria, Subcategoria
from app.utilidades import requiere_rol

ROLES_GESTION = ("Gerente", "Administrador", "Empleado")


@categorias_bp.route("/")
@login_required
@requiere_rol(*ROLES_GESTION)
def listar():
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    return render_template("categorias/listar.html", categorias=categorias)


@categorias_bp.route("/nueva", methods=["GET", "POST"])
@login_required
@requiere_rol(*ROLES_GESTION)
def nueva():
    formulario = CategoriaForm()
    if formulario.validate_on_submit():
        if Categoria.query.filter_by(nombre=formulario.nombre.data.strip()).first():
            flash("Ya existe una categoría con ese nombre.", "danger")
        else:
            db.session.add(Categoria(nombre=formulario.nombre.data.strip(), activo=formulario.activo.data))
            db.session.commit()
            flash("Categoría creada correctamente.", "success")
            return redirect(url_for("categorias.listar"))
    return render_template("categorias/formulario_categoria.html", formulario=formulario, modo="nueva")


@categorias_bp.route("/<int:categoria_id>/editar", methods=["GET", "POST"])
@login_required
@requiere_rol(*ROLES_GESTION)
def editar(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)
    formulario = CategoriaForm(obj=categoria)
    if formulario.validate_on_submit():
        categoria.nombre = formulario.nombre.data.strip()
        categoria.activo = formulario.activo.data
        db.session.commit()
        flash("Categoría actualizada correctamente.", "success")
        return redirect(url_for("categorias.listar"))
    return render_template("categorias/formulario_categoria.html", formulario=formulario, modo="editar", categoria=categoria)


@categorias_bp.route("/subcategorias")
@login_required
@requiere_rol(*ROLES_GESTION)
def listar_subcategorias():
    subcategorias = Subcategoria.query.join(Categoria).order_by(Categoria.nombre, Subcategoria.nombre).all()
    return render_template("categorias/listar_subcategorias.html", subcategorias=subcategorias)


@categorias_bp.route("/subcategorias/nueva", methods=["GET", "POST"])
@login_required
@requiere_rol(*ROLES_GESTION)
def nueva_subcategoria():
    formulario = SubcategoriaForm()
    formulario.categoria_id.choices = [(c.id, c.nombre) for c in Categoria.query.order_by(Categoria.nombre).all()]

    if formulario.validate_on_submit():
        existe = Subcategoria.query.filter_by(
            nombre=formulario.nombre.data.strip(), categoria_id=formulario.categoria_id.data
        ).first()
        if existe:
            flash("Ya existe esa subcategoría dentro de la categoría seleccionada.", "danger")
        else:
            db.session.add(Subcategoria(
                nombre=formulario.nombre.data.strip(),
                categoria_id=formulario.categoria_id.data,
                activo=formulario.activo.data,
            ))
            db.session.commit()
            flash("Subcategoría creada correctamente.", "success")
            return redirect(url_for("categorias.listar_subcategorias"))

    return render_template("categorias/formulario_subcategoria.html", formulario=formulario, modo="nueva")


@categorias_bp.route("/subcategorias/<int:subcategoria_id>/editar", methods=["GET", "POST"])
@login_required
@requiere_rol(*ROLES_GESTION)
def editar_subcategoria(subcategoria_id):
    subcategoria = Subcategoria.query.get_or_404(subcategoria_id)
    formulario = SubcategoriaForm(obj=subcategoria)
    formulario.categoria_id.choices = [(c.id, c.nombre) for c in Categoria.query.order_by(Categoria.nombre).all()]

    if formulario.validate_on_submit():
        subcategoria.nombre = formulario.nombre.data.strip()
        subcategoria.categoria_id = formulario.categoria_id.data
        subcategoria.activo = formulario.activo.data
        db.session.commit()
        flash("Subcategoría actualizada correctamente.", "success")
        return redirect(url_for("categorias.listar_subcategorias"))

    return render_template(
        "categorias/formulario_subcategoria.html", formulario=formulario, modo="editar", subcategoria=subcategoria
    )
