from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from models import Cliente, Mesa, Reservacion
from core.seguridad import permiso_requerido
from services.reservaciones import (
    cancelar_reservacion,
    eliminar_reservacion,
    guardar_reservacion,
)
from services.validaciones import convertir_entero_positivo, convertir_fecha, convertir_hora


reservaciones_bp = Blueprint("reservaciones", __name__, url_prefix="/reservaciones")


@reservaciones_bp.route("")
@permiso_requerido("reservaciones.ver")
def listar():
    return render_template(
        "reservaciones.html",
        reservaciones=Reservacion.query.order_by(
            Reservacion.fecha.desc(),
            Reservacion.hora_reserva,
        ).all(),
        clientes=Cliente.query.order_by(Cliente.nombre).all(),
        mesas=Mesa.query.filter_by(activo=True).order_by(Mesa.numero_mesa).all(),
    )


@reservaciones_bp.post("/guardar")
@permiso_requerido("reservaciones.gestionar")
def guardar():
    formulario = request.form
    try:
        guardar_reservacion(
            id_reservacion=formulario.get("id_reservacion", type=int),
            id_empleado=g.usuario.id_empleado if g.usuario else None,
            id_mesa=convertir_entero_positivo(formulario.get("id_mesa"), "La mesa"),
            personas=convertir_entero_positivo(
                formulario.get("cantidad_personas"),
                "La cantidad de personas",
            ),
            fecha=convertir_fecha(formulario.get("fecha"), "La fecha"),
            hora=convertir_hora(formulario.get("hora_reserva"), "La hora"),
            estado=formulario.get("estado", "Confirmada"),
            id_cliente=formulario.get("id_cliente", type=int),
            cliente_nuevo={
                "nombre": formulario.get("nuevo_cliente_nombre", ""),
                "telefono": formulario.get("nuevo_cliente_telefono", ""),
                "email": formulario.get("nuevo_cliente_email", ""),
                "direccion": formulario.get("nuevo_cliente_direccion", ""),
            },
        )
        flash("Reservación guardada.", "success")
    except (ValueError, LookupError) as error:
        flash(str(error), "danger")
    return redirect(url_for("reservaciones.listar"))


@reservaciones_bp.post("/<int:id_reservacion>/cancelar")
@permiso_requerido("reservaciones.gestionar")
def cancelar(id_reservacion):
    try:
        cancelar_reservacion(id_reservacion)
        flash("Reservación cancelada.", "success")
    except LookupError:
        abort(404)
    return redirect(url_for("reservaciones.listar"))


@reservaciones_bp.post("/<int:id_reservacion>/eliminar")
@permiso_requerido("reservaciones.gestionar")
def eliminar(id_reservacion):
    try:
        eliminar_reservacion(id_reservacion)
        flash(
            "Reservación eliminada. El cliente se eliminó si no tenía otras reservas.",
            "success",
        )
    except LookupError:
        abort(404)
    return redirect(url_for("reservaciones.listar"))
