from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from ...extensions import db
from ...models import Vendedor, Categoria
from .forms import VendedorForm

bp = Blueprint("vendedores", __name__, url_prefix="/vendedores", template_folder="templates")


@bp.route("/")
@login_required
def index():
    vendedores = Vendedor.query.order_by(Vendedor.created_at.desc()).all()
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    form = VendedorForm()
    form.categoria_id.choices = [(0, "-")] + [(c.id, c.nombre) for c in categorias]
    return render_template("vendedores/index.html", vendedores=vendedores, form=form)


@bp.route("/create", methods=["POST"]) 
@login_required
def create():
    form = VendedorForm()
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    form.categoria_id.choices = [(0, "-")] + [(c.id, c.nombre) for c in categorias]
    if form.validate_on_submit():
        cat_id = form.categoria_id.data or 0
        vendedor = Vendedor(
            nombre=form.nombre.data,
            rut=form.rut.data,
            telefono=form.telefono.data,
            correo=form.correo.data,
            categoria_id=(cat_id if cat_id != 0 else None),
        )
        db.session.add(vendedor)
        db.session.commit()
        flash("Vendedor creado", "success")
    else:
        flash("Errores en el formulario", "danger")
    return redirect(url_for("vendedores.index"))


@bp.route("/<int:vendedor_id>/edit", methods=["POST"]) 
@login_required
def edit(vendedor_id: int):
    vendedor = Vendedor.query.get_or_404(vendedor_id)
    form = VendedorForm()
    if form.validate_on_submit():
        cat_id = form.categoria_id.data or 0
        vendedor.nombre = form.nombre.data
        vendedor.rut = form.rut.data
        vendedor.telefono = form.telefono.data
        vendedor.correo = form.correo.data
        vendedor.categoria_id = (cat_id if cat_id != 0 else None)
        db.session.commit()
        flash("Vendedor actualizado", "success")
    else:
        flash("Errores en el formulario", "danger")
    return redirect(url_for("vendedores.index"))


@bp.route("/<int:vendedor_id>/delete", methods=["POST"]) 
@login_required
def delete(vendedor_id: int):
    vendedor = Vendedor.query.get_or_404(vendedor_id)
    db.session.delete(vendedor)
    db.session.commit()
    flash("Vendedor eliminado", "success")
    return redirect(url_for("vendedores.index"))