from datetime import date
from decimal import Decimal
from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func

from ...extensions import db
from ...models import Orden, Pago, NotificationLog

bp = Blueprint("dashboard", __name__, url_prefix="/", template_folder="templates")


@bp.route("/")
@login_required
def index():
    today = date.today()
    total_ventas = db.session.query(func.coalesce(func.sum(Orden.precio_total), 0)).scalar() or Decimal(0)
    total_pagos = db.session.query(func.coalesce(func.sum(Pago.monto), 0)).scalar() or Decimal(0)
    pendientes = db.session.query(func.count(Orden.id)).filter((Orden.precio_total - Orden.abono_calc) > 0).scalar() or 0
    notificaciones = NotificationLog.query.order_by(NotificationLog.created_at.desc()).limit(10).all()
    return render_template("dashboard/index.html", total_ventas=total_ventas, total_pagos=total_pagos, pendientes=pendientes, notificaciones=notificaciones)