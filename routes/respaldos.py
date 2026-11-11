from flask import Blueprint, flash, redirect, render_template, request, url_for

from core.seguridad import permiso_requerido
from services.respaldos import datos_respaldos, generar_respaldo


respaldos_bp = Blueprint("respaldos", __name__, url_prefix="/respaldos")


@respaldos_bp.route("")
@permiso_requerido("respaldos.ver")
def listar():
    return render_template("respaldos.html", **datos_respaldos())


@respaldos_bp.post("/generar")
@permiso_requerido("respaldos.gestionar")
def generar():
    verificar = request.form.get("verificar") == "1"
    try:
        resultado = generar_respaldo(
            request.form.get("tipo", ""),
            descripcion=request.form.get("descripcion", ""),
            verificar=verificar,
        )
        if resultado["estado"] == "EXITOSO":
            categoria = "warning" if verificar and not resultado["verificado"] else "success"
            flash(f"{resultado['mensaje']} Archivo: {resultado['archivo']}", categoria)
        else:
            flash(resultado["mensaje"], "danger")
    except ValueError as error:
        flash(str(error), "danger")
    return redirect(url_for("respaldos.listar"))
