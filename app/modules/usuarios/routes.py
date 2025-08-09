from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from ...extensions import db
from ...models import Usuario
from .forms import LoginForm, UsuarioForm

bp = Blueprint("usuarios", __name__, url_prefix="/usuarios", template_folder="templates")


@bp.route("/login", methods=["GET", "POST"]) 
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Bienvenido", "success")
            return redirect(url_for("dashboard.index"))
        flash("Credenciales inválidas", "danger")
    return render_template("usuarios/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada", "success")
    return redirect(url_for("usuarios.login"))


@bp.route("/")
@login_required
def index():
    if current_user.rol != "admin":
        flash("Solo admin", "warning")
        return redirect(url_for("dashboard.index"))
    usuarios = Usuario.query.order_by(Usuario.created_at.desc()).all()
    form = UsuarioForm()
    return render_template("usuarios/index.html", usuarios=usuarios, form=form)


@bp.route("/create", methods=["POST"]) 
@login_required
def create():
    if current_user.rol != "admin":
        flash("Solo admin", "warning")
        return redirect(url_for("usuarios.index"))
    form = UsuarioForm()
    if form.validate_on_submit():
        if Usuario.query.filter_by(email=form.email.data).first():
            flash("Email ya existe", "danger")
            return redirect(url_for("usuarios.index"))
        user = Usuario(nombre=form.nombre.data, email=form.email.data, rol=form.rol.data)
        if form.password.data:
            user.set_password(form.password.data)
        else:
            user.set_password("changeme123")
        db.session.add(user)
        db.session.commit()
        flash("Usuario creado", "success")
    else:
        flash("Errores en el formulario", "danger")
    return redirect(url_for("usuarios.index"))


@bp.route("/<int:user_id>/edit", methods=["POST"]) 
@login_required
def edit(user_id: int):
    if current_user.rol != "admin":
        flash("Solo admin", "warning")
        return redirect(url_for("usuarios.index"))
    user = Usuario.query.get_or_404(user_id)
    form = UsuarioForm()
    if form.validate_on_submit():
        user.nombre = form.nombre.data
        user.email = form.email.data
        user.rol = form.rol.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash("Usuario actualizado", "success")
    else:
        flash("Errores en el formulario", "danger")
    return redirect(url_for("usuarios.index"))


@bp.route("/<int:user_id>/delete", methods=["POST"]) 
@login_required
def delete(user_id: int):
    if current_user.rol != "admin":
        flash("Solo admin", "warning")
        return redirect(url_for("usuarios.index"))
    user = Usuario.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("Usuario eliminado", "success")
    return redirect(url_for("usuarios.index"))