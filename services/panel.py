from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import func

from models import Mesa, Pago, Produccion, Reservacion, Ticket
from core.base_datos import db
from services.inventario import productos_bajo_stock
from services.mesas import mesas_disponibles


def _grafico_ingresos(hoy, con_datos):
    primer_dia = hoy - timedelta(days=6)
    filas = (
        db.session.query(Pago.fecha, func.sum(Pago.monto_total))
        .filter(Pago.fecha.between(primer_dia, hoy))
        .group_by(Pago.fecha)
        .all()
        if con_datos
        else []
    )
    por_dia = {fila[0]: fila[1] for fila in filas}
    return [
        {
            "etiqueta": (primer_dia + timedelta(days=indice)).strftime("%d/%m"),
            "valor": float(por_dia.get(primer_dia + timedelta(days=indice), Decimal("0"))),
        }
        for indice in range(7)
    ]


def _actividad_reciente(puede):
    actividad = []
    if puede("caja.ver") or puede("reportes.ver"):
        for pago in Pago.query.order_by(Pago.fecha.desc(), Pago.hora.desc()).limit(5):
            actividad.append(
                {
                    "icono": "receipt",
                    "texto": f"Ticket #{pago.id_ticket} cobrado",
                    "detalle": f"₡{pago.monto_total:,.2f}",
                    "momento": datetime.combine(pago.fecha, pago.hora),
                }
            )
    if puede("cocina.ver"):
        producciones = Produccion.query.order_by(
            Produccion.fecha.desc(), Produccion.hora.desc()
        ).limit(5)
        for produccion in producciones:
            actividad.append(
                {
                    "icono": "box-seam",
                    "texto": f"Inventario actualizado: {produccion.producto.nombre}",
                    "detalle": f"+{produccion.cantidad_producida_unidades} unidades",
                    "momento": datetime.combine(produccion.fecha, produccion.hora),
                }
            )
    if puede("reservaciones.ver"):
        reservaciones = Reservacion.query.filter_by(estado="Confirmada").order_by(
            Reservacion.fecha.desc(), Reservacion.hora_reserva.desc()
        ).limit(5)
        for reservacion in reservaciones:
            actividad.append(
                {
                    "icono": "calendar-check",
                    "texto": f"Reservación #{reservacion.id_reservacion}",
                    "detalle": f"{reservacion.cantidad_personas} personas",
                    "momento": datetime.combine(
                        reservacion.fecha, reservacion.hora_reserva or time.min
                    ),
                }
            )
    actividad.sort(key=lambda elemento: elemento["momento"], reverse=True)
    return actividad[:6]


def datos_panel(usuario):
    puede = usuario.tiene_permiso
    hoy = date.today()

    alertas = productos_bajo_stock() if puede("cocina.ver") else []
    ingresos = Decimal("0.00")
    if puede("reportes.ver"):
        ingresos = (
            db.session.query(func.coalesce(func.sum(Pago.monto_total), 0))
            .filter(Pago.fecha == hoy)
            .scalar()
            or Decimal("0.00")
        )
    reservaciones_hoy = (
        Reservacion.query.filter(
            Reservacion.fecha == hoy, Reservacion.estado == "Confirmada"
        ).count()
        if puede("reservaciones.ver")
        else 0
    )
    produccion_hoy = (
        db.session.query(
            func.coalesce(func.sum(Produccion.cantidad_producida_unidades), 0)
        )
        .filter(Produccion.fecha == hoy)
        .scalar()
        or 0
        if puede("cocina.ver")
        else 0
    )

    return {
        "pendientes": Ticket.query.filter_by(estado="Pendiente").count(),
        "mesas_disponibles": len(mesas_disponibles()) if puede("mesas.ver") else 0,
        "mesas_totales": (
            Mesa.query.filter(Mesa.activo == True).count() if puede("mesas.ver") else 0
        ),
        "alertas": len(alertas),
        "productos_alerta": alertas[:5],
        "ingresos": ingresos,
        "reservaciones": reservaciones_hoy,
        "produccion_hoy": produccion_hoy,
        "grafico_ingresos": _grafico_ingresos(hoy, puede("reportes.ver")),
        "actividad_reciente": _actividad_reciente(puede),
    }
