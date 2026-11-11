from datetime import datetime, timedelta

from models import Mesa, Reservacion, Ticket
from core.base_datos import db


DURACION_RESERVACION = timedelta(hours=2)


def guardar_mesa(id_mesa, *, numero, capacidad):
    try:
        mesa = db.session.get(Mesa, id_mesa) if id_mesa else Mesa()
        if id_mesa and not mesa:
            raise LookupError("La mesa no existe.")
        mesa.numero_mesa = numero
        mesa.capacidad = capacidad
        mesa.activo = True
        db.session.add(mesa)
        db.session.commit()
        return mesa
    except Exception:
        db.session.rollback()
        raise


def eliminar_mesa(id_mesa):
    try:
        mesa = db.session.get(Mesa, id_mesa)
        if not mesa:
            raise LookupError("La mesa no existe.")
        if mesa.tickets or mesa.reservaciones:
            mesa.activo = False
            resultado = "archivada"
        else:
            db.session.delete(mesa)
            resultado = "eliminada"
        db.session.commit()
        return resultado
    except Exception:
        db.session.rollback()
        raise


def reservacion_bloquea_mesa(reservacion, momento=None):
    if reservacion.estado != "Confirmada":
        return False
    momento = momento or datetime.now()
    inicio = datetime.combine(reservacion.fecha, reservacion.hora_reserva)
    return inicio <= momento < inicio + DURACION_RESERVACION


def ids_mesas_ocupadas(momento=None):
    momento = momento or datetime.now()
    ocupadas = {
        fila[0]
        for fila in db.session.query(Ticket.id_mesa)
        .filter(
            Ticket.id_mesa.isnot(None),
            Ticket.estado == "Pagado",
            Ticket.fecha_hora_fin.is_(None),
        )
        .all()
    }
    reservaciones = Reservacion.query.filter_by(
        fecha=momento.date(),
        estado="Confirmada",
    ).all()
    ocupadas.update(
        reservacion.id_mesa
        for reservacion in reservaciones
        if reservacion_bloquea_mesa(reservacion, momento)
    )
    return ocupadas


def mesas_disponibles(momento=None):
    ocupadas = ids_mesas_ocupadas(momento)
    consulta = Mesa.query.filter(Mesa.activo == True)
    if ocupadas:
        consulta = consulta.filter(~Mesa.id_mesa.in_(ocupadas))
    return consulta.order_by(Mesa.numero_mesa).all()


def mesa_disponible(id_mesa, momento=None):
    mesa = db.session.get(Mesa, id_mesa)
    return bool(mesa and mesa.activo and id_mesa not in ids_mesas_ocupadas(momento))
