from flask import Blueprint, abort, render_template
from sqlalchemy import text

from models import (
    AuditoriaCaja,
    AuditoriaSeguridad,
    AuditoriaSesion,
    Empleado,
    HistorialDetalleTicket,
    HistorialProducto,
    HistorialReservacion,
    Permiso,
    Rol,
    Ticket,
)
from core.base_datos import db
from core.seguridad import permiso_requerido
from services.auditoria import (
    CAMPOS_CAJA,
    CAMPOS_DETALLE,
    CAMPOS_PRODUCTO,
    CAMPOS_RESERVACION,
    CAMPOS_SEGURIDAD,
    cambios,
)


bitacoras_bp = Blueprint("bitacoras", __name__, url_prefix="/bitacoras")

LIMITE_REGISTROS = 100


def _recientes(modelo, columna_fecha):
    return modelo.query.order_by(columna_fecha.desc()).limit(LIMITE_REGISTROS).all()


@bitacoras_bp.route("")
@permiso_requerido("bitacoras.ver")
def listar():
    return render_template(
        "bitacoras.html",
        productos=_recientes(HistorialProducto, HistorialProducto.fecha_cambio),
        reservaciones=_recientes(HistorialReservacion, HistorialReservacion.fecha_cambio),
        detalles=_recientes(HistorialDetalleTicket, HistorialDetalleTicket.fecha_cambio),
        caja=_recientes(AuditoriaCaja, AuditoriaCaja.fecha_hora),
        seguridad=_recientes(AuditoriaSeguridad, AuditoriaSeguridad.fecha_hora),
        sesiones=_recientes(AuditoriaSesion, AuditoriaSesion.fecha_hora),
        intentos_fallidos=db.session.execute(
            text(
                "SELECT correo, intentosFallidos, ultimoIntento "
                "FROM dbo.vIntentosFallidosRecientes ORDER BY intentosFallidos DESC"
            )
        ).all(),
        empleados={e.id_empleado: e.nombre for e in Empleado.query.all()},
        roles={r.id_rol: r.nombre for r in Rol.query.all()},
        permisos={p.id_permiso: p.nombre for p in Permiso.query.all()},
        campos={
            "producto": CAMPOS_PRODUCTO,
            "reserva": CAMPOS_RESERVACION,
            "detalle": CAMPOS_DETALLE,
            "caja": CAMPOS_CAJA,
            "seguridad": CAMPOS_SEGURIDAD,
        },
        cambios=cambios,
    )


@bitacoras_bp.route("/tickets/<int:id_ticket>")
@permiso_requerido("bitacoras.ver")
def ticket(id_ticket):
    ticket_auditado = db.session.get(Ticket, id_ticket)
    if not ticket_auditado:
        abort(404)
    return render_template("ticket_auditoria.html", ticket=ticket_auditado)
