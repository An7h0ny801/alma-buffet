from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from models import Cliente
from core.seguridad import permiso_requerido
from services.clientes import eliminar_cliente, guardar_cliente


clientes_bp = Blueprint("clientes", __name__, url_prefix="/clientes")


@clientes_bp.route("")
@permiso_requerido("clientes.ver")
def listar():
    return render_template(
        "clientes.html",
        clientes=Cliente.query.order_by(Cliente.nombre).all(),
    )


@clientes_bp.post("/guardar")
@permiso_requerido("clientes.gestionar")
def guardar():
    try:
        guardar_cliente(
            request.form.get("id_cliente", type=int),
            nombre=request.form.get("nombre", "").strip(),
            telefono=request.form.get("telefono", "").strip(),
            correo=request.form.get("email", "").strip(),
            direccion=request.form.get("direccion", "").strip(),
        )
        flash("Cliente guardado.", "success")
    except (ValueError, LookupError) as error:
        flash(str(error), "danger")
    return redirect(url_for("clientes.listar"))


@clientes_bp.post("/<int:id_cliente>/eliminar")
@permiso_requerido("clientes.gestionar")
def eliminar(id_cliente):
    try:
        eliminar_cliente(id_cliente)
        flash("Cliente eliminado.", "success")
    except LookupError:
        abort(404)
    except ValueError as error:
        flash(str(error), "danger")
    return redirect(url_for("clientes.listar"))
