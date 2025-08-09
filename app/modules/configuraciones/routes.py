from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user

bp = Blueprint("configuraciones", __name__, url_prefix="/configuraciones", template_folder="templates")


@bp.route("/")
@login_required
def index():
    if current_user.rol != "admin":
        flash("Solo admin", "warning")
        return redirect(url_for("dashboard.index"))
    cfg = current_app.config
    return render_template("configuraciones/index.html", cfg=cfg)


@bp.route("/smtp", methods=["POST"]) 
@login_required
def smtp_save():
    if current_user.rol != "admin":
        flash("Solo admin", "warning")
        return redirect(url_for("configuraciones.index"))
    form = request.form
    current_app.config.update(
        SMTP_HOST=form.get("host") or current_app.config.get("SMTP_HOST"),
        SMTP_PORT=int(form.get("port") or current_app.config.get("SMTP_PORT")),
        SMTP_USERNAME=form.get("username") or "",
        SMTP_PASSWORD=form.get("password") or "",
        SMTP_USE_TLS=(form.get("use_tls") or "false").lower() == "true",
        SMTP_FROM=form.get("from_addr") or current_app.config.get("SMTP_FROM"),
    )
    flash("SMTP actualizado (solo en runtime)", "success")
    return redirect(url_for("configuraciones.index"))