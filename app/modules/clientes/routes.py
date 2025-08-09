from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from ...extensions import db
from ...models import Cliente
from .forms import ClienteForm

bp = Blueprint("clientes", __name__, url_prefix="/clientes", template_folder="templates")


@bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    query = Cliente.query
    if q:
        like = f"%{q}%"
        query = query.filter((Cliente.nombre.ilike(like)) | (Cliente.correo.ilike(like)))
    clientes = query.order_by(Cliente.created_at.desc()).all()
    form = ClienteForm()
    return render_template("clientes/index.html", clientes=clientes, form=form, q=q)


@bp.route("/create", methods=["POST"]) 
@login_required
def create():
    form = ClienteForm()
    if form.validate_on_submit():
        cliente = Cliente(
            nombre=form.nombre.data,
            rut=form.rut.data,
            telefono=form.telefono.data,
            correo=form.correo.data,
        )
        db.session.add(cliente)
        db.session.commit()
        flash("Cliente creado", "success")
    else:
        flash("Errores en el formulario", "danger")
    return redirect(url_for("clientes.index"))


@bp.route("/<int:cliente_id>/edit", methods=["POST"]) 
@login_required
def edit(cliente_id: int):
    cliente = Cliente.query.get_or_404(cliente_id)
    form = ClienteForm()
    if form.validate_on_submit():
        cliente.nombre = form.nombre.data
        cliente.rut = form.rut.data
        cliente.telefono = form.telefono.data
        cliente.correo = form.correo.data
        db.session.commit()
        flash("Cliente actualizado", "success")
    else:
        flash("Errores en el formulario", "danger")
    return redirect(url_for("clientes.index"))


@bp.route("/<int:cliente_id>/delete", methods=["POST"]) 
@login_required
def delete(cliente_id: int):
    cliente = Cliente.query.get_or_404(cliente_id)
    db.session.delete(cliente)
    db.session.commit()
    flash("Cliente eliminado", "success")
    return redirect(url_for("clientes.index"))