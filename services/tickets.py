import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select

from models import DetalleTicket, Mesa, Pago, Producto, Ticket
from core.base_datos import BLOQUEO_FILA, db
from core.procedimientos import total_ticket
from services.mesas import mesa_disponible


METODOS_PAGO = ("Efectivo", "SINPE", "Tarjeta")
MODALIDADES = ("local", "llevar")


class TarjetaRechazadaError(ValueError):
    pass


def _ticket_bloqueado(id_ticket):
    return (
        db.session.execute(
            select(Ticket)
            .where(Ticket.id_ticket == id_ticket)
            .with_hint(Ticket, BLOQUEO_FILA, "mssql")
        )
        .scalars()
        .first()
    )


def crear_ticket(id_usuario, cantidades):
    cantidades_pedidas = {}
    for id_producto, cantidad_texto in cantidades.items():
        try:
            cantidad = int(cantidad_texto or 0)
        except (TypeError, ValueError) as error:
            raise ValueError("Las cantidades deben ser números enteros.") from error
        if cantidad < 0:
            raise ValueError("Las cantidades no pueden ser negativas.")
        if cantidad:
            cantidades_pedidas[int(id_producto)] = cantidad

    if not cantidades_pedidas:
        raise ValueError("Debe seleccionar al menos un producto.")

    try:
        productos = (
            db.session.execute(
                select(Producto)
                .where(
                    Producto.id_producto.in_(cantidades_pedidas),
                    Producto.activo == True,
                )
                .with_hint(Producto, BLOQUEO_FILA, "mssql")
            )
            .scalars()
            .all()
        )
        if len(productos) != len(cantidades_pedidas):
            raise ValueError("Uno de los productos seleccionados no existe o está inactivo.")

        vasos_gratuitos = 0
        for producto in productos:
            cantidad = cantidades_pedidas[producto.id_producto]
            if producto.stock_unidades < cantidad:
                raise ValueError(
                    f"No hay stock suficiente de {producto.nombre}. "
                    f"Disponibles: {producto.stock_unidades}."
                )
            if producto.es_fresco_gratuito:
                vasos_gratuitos += cantidad
        if vasos_gratuitos > 1:
            raise ValueError("Solo se permite un vaso de fresco gratuito por ticket.")

        ticket = Ticket(id_usuario=id_usuario, estado="Pendiente")
        db.session.add(ticket)
        db.session.flush()
        for producto in productos:
            cantidad = cantidades_pedidas[producto.id_producto]
            producto.stock_unidades -= cantidad
            db.session.add(
                DetalleTicket(
                    ticket=ticket,
                    producto=producto,
                    cantidad_unidades=cantidad,
                    precio_unidad=producto.precio_unidad,
                    subtotal=producto.precio_unidad * cantidad,
                )
            )
        db.session.commit()
        return ticket
    except Exception:
        db.session.rollback()
        raise


def procesar_pago(
    id_ticket,
    metodo_pago,
    modalidad,
    id_mesa=None,
    resultado_tarjeta="aprobado",
    referencia=None,
):
    if metodo_pago not in METODOS_PAGO:
        raise ValueError("Método de pago inválido.")
    if modalidad not in MODALIDADES:
        raise ValueError("Modalidad inválida.")
    if metodo_pago == "Tarjeta" and resultado_tarjeta == "rechazado":
        raise TarjetaRechazadaError(
            "El datáfono rechazó la transacción. El ticket sigue pendiente."
        )

    try:
        ticket = _ticket_bloqueado(id_ticket)
        if not ticket:
            raise LookupError("El ticket no existe.")
        if ticket.estado != "Pendiente" or ticket.pago:
            raise ValueError("El ticket ya tiene un pago.")

        if modalidad == "local":
            if not id_mesa:
                raise ValueError("Debe seleccionar una mesa.")
            mesa = db.session.get(Mesa, int(id_mesa))
            if not mesa or not mesa_disponible(mesa.id_mesa):
                raise ValueError("La mesa seleccionada ya no está disponible.")
            ticket.id_mesa = mesa.id_mesa
            ticket.fecha_hora_fin = None
        else:
            ticket.id_mesa = None
            ticket.fecha_hora_fin = datetime.now()

        referencia_pago = referencia.strip() if referencia else None
        if metodo_pago == "Tarjeta":
            referencia_pago = f"DATA-{uuid.uuid4().hex[:10].upper()}"

        ticket.estado = "Pagado"
        db.session.add(
            Pago(
                ticket=ticket,
                monto_total=Decimal(total_ticket(ticket.id_ticket)),
                metodo_pago=metodo_pago,
                referencia=referencia_pago,
            )
        )
        db.session.commit()
        return ticket
    except Exception:
        db.session.rollback()
        raise


def anular_ticket(id_ticket):
    try:
        ticket = _ticket_bloqueado(id_ticket)
        if not ticket:
            raise LookupError("El ticket no existe.")
        if ticket.estado != "Pendiente":
            raise ValueError("Solo se pueden anular tickets pendientes.")
        for detalle in ticket.detalles:
            detalle.producto.stock_unidades += detalle.cantidad_unidades
        ticket.estado = "Anulado"
        ticket.fecha_hora_fin = datetime.now()
        db.session.commit()
        return ticket
    except Exception:
        db.session.rollback()
        raise


def liberar_mesa(id_mesa):
    try:
        ticket = (
            db.session.execute(
                select(Ticket)
                .where(
                    Ticket.id_mesa == id_mesa,
                    Ticket.estado == "Pagado",
                    Ticket.fecha_hora_fin.is_(None),
                )
                .order_by(Ticket.id_ticket.desc())
                .with_hint(Ticket, BLOQUEO_FILA, "mssql")
            )
            .scalars()
            .first()
        )
        if not ticket:
            raise ValueError("La mesa no tiene un consumo activo.")
        ticket.fecha_hora_fin = datetime.now()
        db.session.commit()
        return ticket
    except Exception:
        db.session.rollback()
        raise
