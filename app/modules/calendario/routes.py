from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint("calendario", __name__, url_prefix="/calendario", template_folder="templates")


@bp.route("/")
@login_required
def index():
    return render_template("calendario/index.html")