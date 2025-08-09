from decimal import Decimal
from io import BytesIO

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user

from ...extensions import db
from ...models import Orden, Cliente, Vendedor, Usuario
from .forms import OrdenForm

bp = Blueprint("ordenes", __name__, url_prefix="/ordenes", template_folder="templates")


@bp.route("/")
@login_required
def index():
    ordenes = Orden.query.order_by(Orden.created_at.desc()).all()
    clientes = Cliente.query.order_by(Cliente.nombre).all()
    vendedores = Vendedor.query.order_by(Vendedor.nombre).all()
    usuarios = Usuario.query.order_by(Usuario.nombre).all()

    form = OrdenForm()
    form.cliente_id.choices = [(c.id, c.nombre) for c in clientes]
    form.vendedor_id.choices = [(0, "-")] + [(v.id, v.nombre) for v in vendedores]
    form.usuario_id.choices = [(u.id, u.nombre) for u in usuarios]

    return render_template("ordenes/index.html", ordenes=ordenes, form=form)


@bp.route("/create", methods=["POST"]) 
@login_required
def create():
    form = OrdenForm()
    if form.validate_on_submit():
        vendedor_id = form.vendedor_id.data or 0
        orden = Orden(
            cliente_id=form.cliente_id.data,
            vendedor_id=(vendedor_id if vendedor_id != 0 else None),
            usuario_id=form.usuario_id.data,
            fecha=form.fecha.data,
            precio_neto=Decimal(form.precio_neto.data or 0),
            iva=Decimal(form.iva.data or 0),
            precio_total=Decimal(form.precio_total.data or 0),
            observaciones=form.observaciones.data,
        )
        db.session.add(orden)
        db.session.commit()
        flash("Orden creada", "success")
    else:
        flash("Errores en el formulario", "danger")
    return redirect(url_for("ordenes.index"))


@bp.route("/<int:orden_id>/edit", methods=["POST"]) 
@login_required
def edit(orden_id: int):
    orden = Orden.query.get_or_404(orden_id)
    form = OrdenForm()
    if form.validate_on_submit():
        vendedor_id = form.vendedor_id.data or 0
        orden.cliente_id = form.cliente_id.data
        orden.vendedor_id = (vendedor_id if vendedor_id != 0 else None)
        orden.usuario_id = form.usuario_id.data
        orden.fecha = form.fecha.data
        orden.precio_neto = Decimal(form.precio_neto.data or 0)
        orden.iva = Decimal(form.iva.data or 0)
        orden.precio_total = Decimal(form.precio_total.data or 0)
        orden.observaciones = form.observaciones.data
        db.session.commit()
        flash("Orden actualizada", "success")
    else:
        flash("Errores en el formulario", "danger")
    return redirect(url_for("ordenes.index"))


@bp.route("/<int:orden_id>/delete", methods=["POST"]) 
@login_required
def delete(orden_id: int):
    orden = Orden.query.get_or_404(orden_id)
    db.session.delete(orden)
    db.session.commit()
    flash("Orden eliminada", "success")
    return redirect(url_for("ordenes.index"))


@bp.route("/<int:orden_id>/print")
@login_required
def print_view(orden_id: int):
    orden = Orden.query.get_or_404(orden_id)
    return render_template("ordenes/print.html", orden=orden)


@bp.route("/<int:orden_id>/pdf")
@login_required
def pdf(orden_id: int):
    # Simple PDF stub using browser print; real PDF via xhtml2pdf could be added later
    orden = Orden.query.get_or_404(orden_id)
    html = render_template("ordenes/print.html", orden=orden)
    try:
        from xhtml2pdf import pisa
        result = BytesIO()
        pisa.CreatePDF(src=html, dest=result)  # noqa: S602
        result.seek(0)
        return send_file(result, as_attachment=True, download_name=f"orden_{orden.id}.pdf", mimetype="application/pdf")
    except Exception:
        flash("No se pudo generar PDF, use la vista imprimible.", "warning")
        return redirect(url_for("ordenes.print_view", orden_id=orden.id))