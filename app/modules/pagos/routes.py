from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from ...extensions import db
from ...models import Pago, Orden
from .forms import PagoForm

bp = Blueprint("pagos", __name__, url_prefix="/pagos", template_folder="templates")


@bp.route("/")
@login_required
def index():
    pagos = Pago.query.order_by(Pago.created_at.desc()).all()
    ordenes = Orden.query.order_by(Orden.created_at.desc()).all()
    form = PagoForm()
    form.orden_id.choices = [(o.id, f"#{o.id} - {o.cliente.nombre}") for o in ordenes]
    return render_template("pagos/index.html", pagos=pagos, form=form)


@bp.route("/create", methods=["POST"]) 
@login_required
def create():
    form = PagoForm()
    if form.validate_on_submit():
        pago = Pago(
            orden_id=form.orden_id.data,
            monto=Decimal(form.monto.data or 0),
            fecha=form.fecha.data,
            metodo=form.metodo.data,
            usuario_id=current_user.id,
        )
        db.session.add(pago)
        db.session.commit()
        flash("Pago registrado", "success")
    else:
        flash("Errores en el formulario", "danger")
    return redirect(url_for("pagos.index"))


@bp.route("/<int:pago_id>/delete", methods=["POST"]) 
@login_required
def delete(pago_id: int):
    pago = Pago.query.get_or_404(pago_id)
    db.session.delete(pago)
    db.session.commit()
    flash("Pago eliminado", "success")
    return redirect(url_for("pagos.index"))