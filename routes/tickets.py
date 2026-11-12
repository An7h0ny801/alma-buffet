from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from models import Mesa, Producto, Ticket
from core.base_datos import db
from core.seguridad import algun_permiso_requerido, permiso_requerido, usuario_puede
from services.mesas import mesas_disponibles
from services.tickets import (
    TarjetaRechazadaError,
    anular_ticket,
    crear_ticket,
    procesar_pago as procesar_pago_ticket,
    totales_caja,
)


tickets_bp = Blueprint("tickets", __name__)


@tickets_bp.route("/tickets")
@algun_permiso_requerido("mostrador.ver", "caja.ver")
def mostrador():
    if not usuario_puede("mostrador.ver"):
        return redirect(url_for("tickets.caja"))
    productos = Producto.query.filter_by(activo=True).order_by(
        Producto.unidad_medida,
        Producto.nombre,
    ).all()
    return render_template("tickets_nuevo.html", productos=productos)


@tickets_bp.post("/tickets/enviar")
@permiso_requerido("mostrador.gestionar")
def enviar():
    cantidades = {
        clave.removeprefix("cantidad_"): valor
        for clave, valor in request.form.items()
        if clave.startswith("cantidad_")
    }
    try:
        ticket = crear_ticket(session["usuario_id"], cantidades)
        flash(f"Ticket #{ticket.id_ticket} enviado a caja.", "success")
    except ValueError as error:
        flash(str(error), "danger")
    return redirect(url_for("tickets.mostrador"))


@tickets_bp.route("/caja")
@permiso_requerido("caja.ver")
def caja():
    pendientes = Ticket.query.filter_by(estado="Pendiente").order_by(
        Ticket.fecha,
        Ticket.hora_inicio,
    ).all()
    disponibles = mesas_disponibles()
    return render_template(
        "caja.html",
        pendientes=pendientes,
        totales=totales_caja(ticket.id_ticket for ticket in pendientes),
        local_lleno=len(disponibles) == 0,
        mesas_disponibles=len(disponibles),
        mesas_totales=Mesa.query.count(),
    )


@tickets_bp.route("/caja/ticket/<int:id_ticket>")
@permiso_requerido("caja.gestionar")
def cobrar(id_ticket):
    ticket = db.session.get(Ticket, id_ticket)
    if not ticket:
        abort(404)
    if ticket.estado != "Pendiente":
        abort(409, description="El ticket ya fue procesado.")
    return render_template(
        "cobrar_ticket.html",
        ticket=ticket,
        mesas=mesas_disponibles(),
    )


@tickets_bp.post("/caja/ticket/<int:id_ticket>/pagar")
@permiso_requerido("caja.gestionar")
def procesar_pago(id_ticket):
    try:
        procesar_pago_ticket(
            id_ticket,
            metodo_pago=request.form.get("metodo_pago", ""),
            modalidad=request.form.get("modalidad", "llevar"),
            id_mesa=request.form.get("id_mesa", type=int),
            resultado_tarjeta=request.form.get("resultado_tarjeta", "aprobado"),
            referencia=request.form.get("referencia"),
        )
    except LookupError:
        abort(404)
    except (TarjetaRechazadaError, ValueError) as error:
        flash(str(error), "danger")
        return redirect(url_for("tickets.cobrar", id_ticket=id_ticket))
    return redirect(url_for("tickets.factura", id_ticket=id_ticket))


@tickets_bp.post("/tickets/<int:id_ticket>/anular")
@algun_permiso_requerido("mostrador.gestionar", "caja.gestionar")
def anular(id_ticket):
    try:
        ticket = anular_ticket(id_ticket)
    except LookupError:
        abort(404)
    except ValueError as error:
        abort(409, description=str(error))
    flash(f"Ticket #{ticket.id_ticket} anulado; se devolvió el inventario.", "success")
    return redirect(url_for("tickets.caja"))


@tickets_bp.route("/factura/<int:id_ticket>")
@permiso_requerido("caja.ver")
def factura(id_ticket):
    ticket = db.session.get(Ticket, id_ticket)
    if not ticket:
        abort(404)
    if not ticket.pago:
        abort(409, description="El ticket no ha sido pagado.")
    return render_template("factura.html", ticket=ticket)
