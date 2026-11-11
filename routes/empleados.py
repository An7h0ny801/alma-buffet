from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from models import Empleado
from core.seguridad import permiso_requerido
from services.empleados import eliminar_empleado, guardar_empleado
from services.validaciones import convertir_fecha


empleados_bp = Blueprint("empleados", __name__, url_prefix="/empleados")


@empleados_bp.route("")
@permiso_requerido("empleados.ver")
def listar():
    return render_template(
        "empleados.html",
        empleados=Empleado.query.filter(Empleado.es_sistema == False)
        .order_by(Empleado.activo.desc(), Empleado.nombre)
        .all(),
    )


@empleados_bp.post("/guardar")
@permiso_requerido("empleados.gestionar")
def guardar():
    try:
        guardar_empleado(
            request.form.get("id_empleado", type=int),
            nombre=request.form.get("nombre", "").strip(),
            puesto=request.form.get("puesto", "").strip(),
            telefono=request.form.get("telefono", "").strip(),
            fecha_contratacion=convertir_fecha(
                request.form.get("fecha_contratacion"),
                "La fecha de contratación",
            ),
            activo=request.form.get("activo") == "1",
        )
        flash("Empleado guardado.", "success")
    except (ValueError, LookupError) as error:
        flash(str(error), "danger")
    return redirect(url_for("empleados.listar"))


@empleados_bp.post("/<int:id_empleado>/eliminar")
@permiso_requerido("empleados.gestionar")
def eliminar(id_empleado):
    try:
        resultado = eliminar_empleado(
            id_empleado,
            g.usuario.id_empleado if g.usuario else None,
        )
    except LookupError:
        abort(404)
    except ValueError as error:
        flash(str(error), "danger")
        return redirect(url_for("empleados.listar"))
    flash(
        "Empleado eliminado."
        if resultado == "eliminado"
        else "Empleado archivado porque tiene historial o usuario.",
        "success",
    )
    return redirect(url_for("empleados.listar"))
