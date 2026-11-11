from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from models import Empleado, Rol, Usuario
from core.seguridad import permiso_requerido, renovar_huella
from services.acceso import eliminar_usuario, guardar_usuario


usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


@usuarios_bp.route("")
@permiso_requerido("usuarios.gestionar")
def listar():
    return render_template(
        "usuarios.html",
        usuarios=Usuario.query.order_by(Usuario.activo.desc(), Usuario.correo).all(),
        empleados=Empleado.query.filter(
            Empleado.activo == True,
            Empleado.es_sistema == False,
        ).order_by(Empleado.nombre).all(),
        roles=Rol.query.order_by(Rol.nombre).all(),
    )


@usuarios_bp.post("/guardar")
@permiso_requerido("usuarios.gestionar")
def guardar():
    try:
        usuario = guardar_usuario(
            request.form.get("id_usuario", type=int),
            correo=request.form.get("correo", ""),
            id_rol=request.form.get("id_rol", type=int),
            id_empleado=request.form.get("id_empleado", type=int),
            activo=request.form.get("activo", "1") == "1",
            password=request.form.get("password") or None,
            forzar_cambio_password=request.form.get("debe_cambiar_password") == "1",
            actor=g.usuario,
        )
        renovar_huella(usuario)
        flash("Usuario guardado.", "success")
    except IntegrityError:
        flash("Ya existe un usuario con ese correo.", "danger")
    except (ValueError, LookupError) as error:
        flash(str(error), "danger")
    return redirect(url_for("usuarios.listar"))


@usuarios_bp.post("/<int:id_usuario>/eliminar")
@permiso_requerido("usuarios.gestionar")
def eliminar(id_usuario):
    try:
        eliminar_usuario(id_usuario, actor=g.usuario)
        flash("Usuario eliminado o desactivado según su historial.", "success")
    except LookupError:
        abort(404)
    except ValueError as error:
        flash(str(error), "danger")
    return redirect(url_for("usuarios.listar"))
