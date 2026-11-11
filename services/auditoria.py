from flask import current_app, request
from sqlalchemy import text

from core.base_datos import db
from core.procedimientos import ejecutar_procedimiento


LOGIN_OK = "LOGIN_OK"
LOGIN_FALLIDO = "LOGIN_FALLIDO"
LOGOUT = "LOGOUT"

_INTENTOS_RECIENTES = text(
    "SELECT "
    "(SELECT COUNT(*) FROM dbo.TblAuditoriaSesiones AS s "
    " WHERE s.correo = :correo AND s.evento = 'LOGIN_FALLIDO' "
    " AND s.fechaHora >= DATEADD(MINUTE, -:minutos, SYSDATETIME()) "
    " AND s.fechaHora > ISNULL((SELECT MAX(o.fechaHora) FROM dbo.TblAuditoriaSesiones AS o "
    "   WHERE o.correo = :correo AND o.evento = 'LOGIN_OK'), '19000101')) AS porCorreo, "
    "(SELECT COUNT(*) FROM dbo.TblAuditoriaSesiones AS s "
    " WHERE s.direccionIp = :ip AND s.evento = 'LOGIN_FALLIDO' "
    " AND s.fechaHora >= DATEADD(MINUTE, -:minutos, SYSDATETIME())) AS porIp"
)


def login_bloqueado(correo):
    configuracion = current_app.config
    fila = db.session.execute(
        _INTENTOS_RECIENTES,
        {
            "correo": (correo or "")[:120],
            "ip": (request.remote_addr or "")[:45],
            "minutos": configuracion["LOGIN_VENTANA_MINUTOS"],
        },
    ).one()
    return (
        fila.porCorreo >= configuracion["LOGIN_MAX_INTENTOS"]
        or fila.porIp >= configuracion["LOGIN_MAX_INTENTOS_IP"]
    )


def registrar_evento_sesion(evento, correo, id_usuario=None):
    try:
        ejecutar_procedimiento(
            "pa_RegistrarEventoSesion",
            pEvento=evento,
            pCorreo=(correo or "")[:120],
            pIdUsuario=id_usuario,
            pDireccionIp=(request.remote_addr or "")[:45] or None,
            pNavegador=(request.user_agent.string or "")[:200] or None,
        )
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("No se pudo registrar el evento de sesión %s", evento)


CAMPOS_PRODUCTO = (
    ("Nombre", "nombre", "nombre_anterior"),
    ("Precio", "precio_unidad", "precio_unidad_anterior"),
    ("Unidad", "unidad_medida", "unidad_medida_anterior"),
    ("Stock", "stock_unidades", "stock_unidades_anterior"),
    ("Activo", "activo", "activo_anterior"),
)
CAMPOS_RESERVACION = (
    ("Cliente", "id_cliente", "id_cliente_anterior"),
    ("Mesa", "id_mesa", "id_mesa_anterior"),
    ("Fecha", "fecha", "fecha_anterior"),
    ("Hora", "hora_reserva", "hora_reserva_anterior"),
    ("Personas", "cantidad_personas", "cantidad_personas_anterior"),
    ("Estado", "estado", "estado_anterior"),
)
CAMPOS_DETALLE = (
    ("Cantidad", "cantidad_unidades", "cantidad_unidades_anterior"),
    ("Precio", "precio_unidad", "precio_unidad_anterior"),
    ("Subtotal", "subtotal", "subtotal_anterior"),
)
CAMPOS_CAJA = (
    ("Estado", "estado_nuevo", "estado_anterior"),
    ("Monto", "monto_nuevo", "monto_anterior"),
    ("Método", "metodo_pago_nuevo", "metodo_pago_anterior"),
    ("Referencia", "referencia_nueva", "referencia_anterior"),
)
CAMPOS_SEGURIDAD = (
    ("Correo", "correo_nuevo", "correo_anterior"),
    ("Rol", "id_rol_nuevo", "id_rol_anterior"),
    ("Activo", "activo_nuevo", "activo_anterior"),
)


def cambios(registro, campos):
    resultado = []
    for etiqueta, nuevo, anterior in campos:
        valor_nuevo = getattr(registro, nuevo)
        valor_anterior = getattr(registro, anterior)
        if valor_anterior is None and valor_nuevo is None:
            continue
        if registro.accion == "UPDATE" and valor_anterior == valor_nuevo:
            continue
        resultado.append((etiqueta, valor_anterior, valor_nuevo))
    return resultado
