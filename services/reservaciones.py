from datetime import datetime

from sqlalchemy import select

from models import Cliente, Empleado, Mesa, Reservacion
from core.base_datos import db
from services.clientes import crear_cliente_sin_confirmar
from services.mesas import DURACION_RESERVACION


ESTADOS_RESERVACION = ("Pendiente", "Confirmada", "Cancelada")


def _validar_reservacion(reservacion, id_reservacion=None):
    mesa = db.session.get(Mesa, reservacion.id_mesa)
    if not mesa:
        raise ValueError("La mesa seleccionada no existe.")
    if reservacion.cantidad_personas > mesa.capacidad:
        raise ValueError("La cantidad de personas supera la capacidad de la mesa.")
    if reservacion.estado not in ESTADOS_RESERVACION:
        raise ValueError("Estado inválido.")

    inicio = datetime.combine(reservacion.fecha, reservacion.hora_reserva)
    otras = (
        db.session.execute(
            select(Reservacion).where(
                Reservacion.id_mesa == reservacion.id_mesa,
                Reservacion.fecha == reservacion.fecha,
                Reservacion.estado == "Confirmada",
            )
        )
        .scalars()
        .all()
    )
    for otra in otras:
        if otra.id_reservacion == id_reservacion:
            continue
        inicio_otra = datetime.combine(otra.fecha, otra.hora_reserva)
        if abs(inicio - inicio_otra) < DURACION_RESERVACION:
            raise ValueError("La mesa ya tiene una reservación en esa franja.")


def guardar_reservacion(
    *,
    id_reservacion,
    id_empleado,
    id_mesa,
    personas,
    fecha,
    hora,
    estado="Confirmada",
    id_cliente=None,
    cliente_nuevo=None,
):
    try:
        reservacion = (
            db.session.get(Reservacion, id_reservacion)
            if id_reservacion
            else Reservacion()
        )
        if id_reservacion and not reservacion:
            raise LookupError("La reservación no existe.")

        if cliente_nuevo and cliente_nuevo.get("nombre", "").strip():
            cliente = crear_cliente_sin_confirmar(
                nombre=cliente_nuevo["nombre"],
                telefono=cliente_nuevo.get("telefono"),
                correo=cliente_nuevo.get("email"),
                direccion=cliente_nuevo.get("direccion"),
            )
            reservacion.id_cliente = cliente.id_cliente
        elif id_cliente:
            if not db.session.get(Cliente, id_cliente):
                raise ValueError("El cliente seleccionado no existe.")
            reservacion.id_cliente = id_cliente
        else:
            raise ValueError("Seleccione un cliente o registre uno nuevo.")

        if not id_empleado:
            empleado = Empleado.query.filter_by(activo=True).first()
            if not empleado:
                raise ValueError("Debe existir un empleado activo.")
            id_empleado = empleado.id_empleado

        reservacion.id_empleado = id_empleado
        reservacion.id_mesa = id_mesa
        reservacion.cantidad_personas = personas
        reservacion.fecha = fecha
        reservacion.hora_reserva = hora
        reservacion.estado = estado
        _validar_reservacion(reservacion, id_reservacion)
        db.session.add(reservacion)
        db.session.commit()
        return reservacion
    except Exception:
        db.session.rollback()
        raise


def cancelar_reservacion(id_reservacion):
    try:
        reservacion = db.session.get(Reservacion, id_reservacion)
        if not reservacion:
            raise LookupError("La reservación no existe.")
        reservacion.estado = "Cancelada"
        db.session.commit()
        return reservacion
    except Exception:
        db.session.rollback()
        raise


def eliminar_reservacion(id_reservacion):
    try:
        reservacion = db.session.get(Reservacion, id_reservacion)
        if not reservacion:
            raise LookupError("La reservación no existe.")
        cliente = reservacion.cliente
        db.session.delete(reservacion)
        db.session.flush()
        if cliente and not Reservacion.query.filter_by(
            id_cliente=cliente.id_cliente
        ).first():
            db.session.delete(cliente)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
