from flask import Blueprint, g, render_template

from core.seguridad import login_requerido
from services.panel import datos_panel


panel_bp = Blueprint("panel", __name__)


@panel_bp.route("/dashboard")
@login_requerido
def inicio():
    return render_template("dashboard.html", **datos_panel(g.usuario))
