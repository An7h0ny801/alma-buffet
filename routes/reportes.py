from io import BytesIO

from flask import Blueprint, abort, make_response, render_template, request
from reportlab.pdfgen import canvas
from sqlalchemy import func

from models import DetalleTicket, Pago, Produccion, Producto, Ticket
from core.base_datos import db
from core.seguridad import permiso_requerido
from services.validaciones import convertir_fecha


reportes_bp = Blueprint("reportes", __name__)


def _rango_fechas():
    desde = request.args.get("desde") or None
    hasta = request.args.get("hasta") or None
    try:
        return (
            convertir_fecha(desde, "La fecha inicial") if desde else None,
            convertir_fecha(hasta, "La fecha final") if hasta else None,
        )
    except ValueError as error:
        abort(400, description=str(error))


def _filtrar_por_fecha(consulta, columna, desde, hasta):
    if desde:
        consulta = consulta.filter(columna >= desde)
    if hasta:
        consulta = consulta.filter(columna <= hasta)
    return consulta


def _respuesta_pdf(buffer, nombre_archivo):
    respuesta = make_response(buffer.getvalue())
    respuesta.headers["Content-Type"] = "application/pdf"
    respuesta.headers["Content-Disposition"] = f"attachment; filename={nombre_archivo}"
    return respuesta


@reportes_bp.route("/reportes")
@permiso_requerido("reportes.ver")
def inicio():
    desde, hasta = _rango_fechas()
    pagos = (
        _filtrar_por_fecha(Pago.query, Pago.fecha, desde, hasta)
        .order_by(Pago.fecha.desc(), Pago.hora.desc())
        .all()
    )
    ingresos = sum((pago.monto_total for pago in pagos), 0)

    productos = (
        _filtrar_por_fecha(
            db.session.query(
                Producto.nombre,
                Producto.unidad_medida,
                func.sum(DetalleTicket.cantidad_unidades).label("cantidad"),
            )
            .join(DetalleTicket, Producto.id_producto == DetalleTicket.id_producto)
            .join(Ticket, Ticket.id_ticket == DetalleTicket.id_ticket)
            .filter(Ticket.estado == "Pagado"),
            Ticket.fecha,
            desde,
            hasta,
        )
        .group_by(Producto.id_producto, Producto.nombre, Producto.unidad_medida)
        .order_by(func.sum(DetalleTicket.cantidad_unidades).desc())
        .all()
    )

    metodos = {}
    for pago in pagos:
        metodos[pago.metodo_pago] = metodos.get(pago.metodo_pago, 0) + 1

    produccion = (
        _filtrar_por_fecha(
            db.session.query(
                Producto.nombre,
                func.sum(Produccion.cantidad_producida_unidades),
            ).join(Produccion, Producto.id_producto == Produccion.id_producto),
            Produccion.fecha,
            desde,
            hasta,
        )
        .group_by(Producto.id_producto, Producto.nombre)
        .all()
    )
    return render_template(
        "reportes.html",
        pagos=pagos,
        ingresos=ingresos,
        productos=productos,
        metodos=metodos,
        produccion=produccion,
        desde=desde.isoformat() if desde else None,
        hasta=hasta.isoformat() if hasta else None,
    )


@reportes_bp.route("/factura_pdf/<int:id_ticket>")
@permiso_requerido("reportes.ver")
def factura_pdf(id_ticket):
    ticket = db.session.get(Ticket, id_ticket)
    if not ticket:
        abort(404)
    if not ticket.pago:
        abort(409, description="El ticket no tiene un pago registrado.")

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    y = 800
    pdf.setTitle(f"Factura {ticket.id_ticket} - Alma Buffet")
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, "ALMA BUFFET")
    y -= 28
    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, y, f"Factura #{ticket.id_ticket}")
    y -= 18
    pdf.drawString(50, y, f"Fecha: {ticket.fecha}  Modalidad: {ticket.modalidad}")
    y -= 18
    if ticket.mesa:
        pdf.drawString(50, y, f"Mesa: {ticket.mesa.numero_mesa}")
        y -= 18
    pdf.line(50, y, 550, y)
    y -= 24
    for detalle in ticket.detalles:
        pdf.drawString(
            50,
            y,
            f"{detalle.cantidad_unidades} x {detalle.producto.nombre} "
            f"({detalle.producto.unidad_medida})",
        )
        pdf.drawRightString(540, y, f"CRC {detalle.subtotal:,.2f}")
        y -= 20
    y -= 10
    pdf.line(50, y, 550, y)
    y -= 22
    pdf.drawRightString(540, y, f"Subtotal: CRC {ticket.subtotal:,.2f}")
    y -= 18
    pdf.drawRightString(540, y, f"IVA 13%: CRC {ticket.impuesto:,.2f}")
    y -= 20
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawRightString(540, y, f"TOTAL: CRC {ticket.pago.monto_total:,.2f}")
    y -= 24
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, y, f"Pago: {ticket.pago.metodo_pago}")
    if ticket.pago.referencia:
        y -= 16
        pdf.drawString(50, y, f"Referencia: {ticket.pago.referencia}")
    pdf.save()
    buffer.seek(0)
    return _respuesta_pdf(buffer, f"factura_{ticket.id_ticket}.pdf")


@reportes_bp.route("/reporte_ventas_pdf")
@permiso_requerido("reportes.ver")
def ventas_pdf():
    desde, hasta = _rango_fechas()
    pagos = (
        _filtrar_por_fecha(Pago.query, Pago.fecha, desde, hasta)
        .order_by(Pago.fecha, Pago.hora)
        .all()
    )
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setTitle("Reporte de ventas - Alma Buffet")
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, 800, "ALMA BUFFET - REPORTE DE VENTAS")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 780, f"Periodo: {desde or 'inicio'} a {hasta or 'hoy'}")
    y = 745
    total = 0
    for pago in pagos:
        pdf.drawString(50, y, f"Ticket #{pago.ticket.id_ticket}")
        pdf.drawString(150, y, str(pago.fecha))
        pdf.drawString(270, y, pago.metodo_pago)
        pdf.drawRightString(540, y, f"CRC {pago.monto_total:,.2f}")
        total += pago.monto_total
        y -= 18
        if y < 70:
            pdf.showPage()
            y = 790
    pdf.line(50, y, 550, y)
    y -= 24
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawRightString(540, y, f"TOTAL: CRC {total:,.2f}")
    pdf.save()
    buffer.seek(0)
    return _respuesta_pdf(buffer, "reporte_ventas.pdf")
