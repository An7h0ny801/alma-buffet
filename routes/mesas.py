from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from models import Mesa, Ticket
from core.seguridad import permiso_requerido, usuario_puede
from services.mesas import eliminar_mesa, guardar_mesa, ids_mesas_ocupadas
from services.tickets import liberar_mesa
from services.validaciones import convertir_entero_positivo


mesas_bp = Blueprint("mesas", __name__, url_prefix="/mesas")


@mesas_bp.route("")
@permiso_requerido("mesas.ver")
def listar():
    consulta = Mesa.query
    if not usuario_puede("mesas.gestionar"):
        consulta = consulta.filter(Mesa.activo == True)
    tickets_activos = {
        ticket.id_mesa: ticket
        for ticket in Ticket.query.filter(
            Ticket.id_mesa.isnot(None),
            Ticket.estado == "Pagado",
            Ticket.fecha_hora_fin.is_(None),
        ).all()
    }
    return render_template(
        "mesas.html",
        mesas=consulta.order_by(Mesa.activo.desc(), Mesa.numero_mesa).all(),
        ocupadas=ids_mesas_ocupadas(),
        tickets_activos=tickets_activos,
    )


@mesas_bp.post("/guardar")
@permiso_requerido("mesas.gestionar")
def guardar():
    try:
        guardar_mesa(
            request.form.get("id_mesa", type=int),
            numero=convertir_entero_positivo(request.form.get("numero_mesa"), "El número"),
            capacidad=convertir_entero_positivo(
                request.form.get("capacidad"), "La capacidad"
            ),
        )
        flash("Mesa guardada.", "success")
    except (ValueError, LookupError, IntegrityError):
        flash("Número de mesa repetido o datos inválidos.", "danger")
    return redirect(url_for("mesas.listar"))


@mesas_bp.post("/<int:id_mesa>/eliminar")
@permiso_requerido("mesas.gestionar")
def eliminar(id_mesa):
    try:
        resultado = eliminar_mesa(id_mesa)
    except LookupError:
        abort(404)
    flash(
        "Mesa eliminada."
        if resultado == "eliminada"
        else "Mesa archivada porque tiene historial.",
        "success",
    )
    return redirect(url_for("mesas.listar"))


@mesas_bp.post("/<int:id_mesa>/liberar")
@permiso_requerido("caja.gestionar")
def liberar(id_mesa):
    try:
        ticket = liberar_mesa(id_mesa)
    except ValueError as error:
        abort(409, description=str(error))
    flash(f"Mesa {ticket.mesa.numero_mesa} liberada.", "success")
    return redirect(url_for("mesas.listar"))
