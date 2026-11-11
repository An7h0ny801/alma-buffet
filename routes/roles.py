from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from models import Permiso, Rol
from core.base_datos import db
from core.seguridad import permiso_requerido
from services.acceso import (
    actualizar_permisos_rol,
    codigos_de_rol,
    eliminar_rol,
    grupos_permisos,
    guardar_rol,
    renombrar_rol,
)


roles_bp = Blueprint("roles", __name__, url_prefix="/roles")


@roles_bp.route("")
@permiso_requerido("roles.gestionar")
def listar():
    roles = Rol.query.order_by(Rol.protegido.desc(), Rol.nombre).all()
    seleccionado = None
    id_rol = request.args.get("rol", type=int)
    if id_rol:
        seleccionado = db.session.get(Rol, id_rol)
        if not seleccionado:
            abort(404)
        if seleccionado.protegido:
            flash("El rol Administrador siempre tiene todos los permisos.", "info")
            return redirect(url_for("roles.listar"))
    permisos = Permiso.query.order_by(Permiso.codigo).all()
    return render_template(
        "roles.html",
        roles=roles,
        seleccionado=seleccionado,
        asignados={p.codigo for p in seleccionado.permisos} if seleccionado else set(),
        grupos=grupos_permisos(permisos),
        total_permisos=len(permisos),
    )


@roles_bp.post("/guardar")
@permiso_requerido("roles.gestionar")
def guardar():
    try:
        codigos = request.form.getlist("permisos")
        id_rol_base = request.form.get("id_rol_base", type=int)
        if id_rol_base:
            codigos += codigos_de_rol(id_rol_base)
        rol = guardar_rol(
            request.form.get("id_rol", type=int),
            nombre=request.form.get("nombre", ""),
            codigos_permisos=codigos,
            actor=g.usuario,
        )
        flash("Rol guardado.", "success")
        if not rol.protegido:
            return redirect(url_for("roles.listar", rol=rol.id_rol))
    except IntegrityError:
        flash("Ya existe un rol con ese nombre.", "danger")
    except (ValueError, LookupError) as error:
        flash(str(error), "danger")
    return redirect(url_for("roles.listar"))


@roles_bp.post("/<int:id_rol>/permisos")
@permiso_requerido("roles.gestionar")
def guardar_permisos(id_rol):
    try:
        if actualizar_permisos_rol(id_rol, request.form.getlist("permisos"), actor=g.usuario):
            flash("Permisos del rol guardados.", "success")
        else:
            flash("No había cambios que guardar.", "info")
    except LookupError:
        abort(404)
    except ValueError as error:
        flash(str(error), "danger")
        return redirect(url_for("roles.listar"))
    return redirect(url_for("roles.listar", rol=id_rol))


@roles_bp.post("/<int:id_rol>/renombrar")
@permiso_requerido("roles.gestionar")
def renombrar(id_rol):
    try:
        renombrar_rol(id_rol, request.form.get("nombre", ""), actor=g.usuario)
        flash("Rol renombrado.", "success")
    except IntegrityError:
        flash("Ya existe un rol con ese nombre.", "danger")
    except LookupError:
        abort(404)
    except ValueError as error:
        flash(str(error), "danger")
    return redirect(url_for("roles.listar", rol=id_rol))


@roles_bp.post("/<int:id_rol>/eliminar")
@permiso_requerido("roles.gestionar")
def eliminar(id_rol):
    try:
        eliminar_rol(id_rol, actor=g.usuario)
        flash("Rol eliminado.", "success")
    except LookupError:
        abort(404)
    except ValueError as error:
        flash(str(error), "danger")
    return redirect(url_for("roles.listar"))
