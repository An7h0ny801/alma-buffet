import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from core.base_datos import db
from core import migraciones
from tests.conftest import BASE_PRUEBAS
from tests.utilidades import (
    CORREO_ADMIN,
    PASSWORD_ADMIN,
    consulta,
    crear_producto,
    crear_ticket,
    crear_usuario,
    enviar,
    iniciar_sesion,
    nombre_unico,
    texto,
    valor,
)


def _id_empleado_admin(app):
    return valor(app, "SELECT idEmpleado FROM TblUsuarios WHERE correo = 'admin@alma.com'")


def _ejecutar(app, sql, **parametros):
    with app.app_context():
        db.session.execute(text(sql), parametros)
        db.session.commit()


def _ultimo(app, sql, **parametros):
    return consulta(app, sql, **parametros)[-1]


def prueba_update_guarda_valor_anterior_y_nuevo(admin):
    app = admin.application
    nombre = nombre_unico("Precio")
    id_producto = crear_producto(admin, nombre=nombre, precio="1500")
    enviar(
        admin,
        "/productos/guardar",
        {
            "id_producto": str(id_producto),
            "nombre": nombre,
            "precio_unidad": "1800",
            "unidad_medida": "Porción",
            "stock_unidades": "20",
            "activo": "1",
        },
    )
    fila = _ultimo(
        app,
        "SELECT accion, precioUnidadAnterior, precioUnidad, idEmpleado, usuarioBD, aplicacion "
        "FROM TblHistorialProductos WHERE idProducto = :p ORDER BY idHistorialProducto",
        p=id_producto,
    )
    assert tuple(fila[:4]) == ("UPDATE", 1500, 1800, _id_empleado_admin(app))
    assert fila.usuarioBD and fila.aplicacion


def prueba_desactivar_producto_registra_activo_anterior(admin):
    app = admin.application
    id_producto = crear_producto(admin)
    enviar(admin, f"/productos/{id_producto}/eliminar")
    fila = _ultimo(
        app,
        "SELECT activoAnterior, activo FROM TblHistorialProductos "
        "WHERE idProducto = :p ORDER BY idHistorialProducto",
        p=id_producto,
    )
    assert tuple(fila) == (True, False)


def prueba_trigger_procesa_varias_filas_en_una_operacion(admin):
    app = admin.application
    ids = ", ".join(str(crear_producto(admin, precio="1000")) for _ in range(3))
    _ejecutar(app, f"UPDATE TblProductos SET precioUnidad = precioUnidad + 250 WHERE idProducto IN ({ids})")
    filas = consulta(
        app,
        "SELECT precioUnidadAnterior, precioUnidad FROM TblHistorialProductos "
        f"WHERE accion = 'UPDATE' AND idProducto IN ({ids})",
    )
    assert [tuple(fila) for fila in filas] == [(1000, 1250)] * 3


def prueba_anulacion_de_ticket_queda_en_auditoria_caja(admin):
    app = admin.application
    id_ticket = crear_ticket(admin, {crear_producto(admin, precio="2000"): 2})
    enviar(admin, f"/tickets/{id_ticket}/anular")
    fila = _ultimo(
        app,
        "SELECT tablaAfectada, accion, estadoAnterior, estadoNuevo, montoTicket, idEmpleado "
        "FROM TblAuditoriaCaja WHERE idTicket = :t ORDER BY idAuditoriaCaja",
        t=id_ticket,
    )
    assert tuple(fila) == ("TblTickets", "UPDATE", "Pendiente", "Anulado", 4520, _id_empleado_admin(app))


def prueba_cobro_de_ticket_queda_en_auditoria_caja(admin):
    app = admin.application
    id_ticket = crear_ticket(admin, {crear_producto(admin): 1})
    enviar(admin, f"/caja/ticket/{id_ticket}/pagar", {"metodo_pago": "Efectivo", "modalidad": "llevar"})
    filas = consulta(
        app,
        "SELECT tablaAfectada, accion, estadoAnterior, estadoNuevo, metodoPagoNuevo, idEmpleado "
        "FROM TblAuditoriaCaja WHERE idTicket = :t ORDER BY tablaAfectada",
        t=id_ticket,
    )
    id_admin = _id_empleado_admin(app)
    assert [tuple(fila) for fila in filas] == [
        ("TblPagos", "INSERT", None, None, "Efectivo", id_admin),
        ("TblTickets", "UPDATE", "Pendiente", "Pagado", None, id_admin),
    ]


def prueba_alterar_un_pago_queda_registrado(admin):
    app = admin.application
    id_ticket = crear_ticket(admin, {crear_producto(admin, precio="1000"): 1})
    enviar(
        admin,
        f"/caja/ticket/{id_ticket}/pagar",
        {"metodo_pago": "SINPE", "modalidad": "llevar", "referencia": "111"},
    )
    _ejecutar(app, "UPDATE TblPagos SET montoTotal = 1, referencia = '999' WHERE idTicket = :t", t=id_ticket)
    _ejecutar(app, "DELETE FROM TblPagos WHERE idTicket = :t", t=id_ticket)
    filas = consulta(
        app,
        "SELECT accion, montoAnterior, montoNuevo, referenciaAnterior, referenciaNueva "
        "FROM TblAuditoriaCaja WHERE tablaAfectada = 'TblPagos' AND idTicket = :t "
        "ORDER BY idAuditoriaCaja",
        t=id_ticket,
    )
    assert [tuple(fila) for fila in filas] == [
        ("INSERT", None, 1130, None, "111"),
        ("UPDATE", 1130, 1, "111", "999"),
        ("DELETE", 1, None, "999", None),
    ]


def prueba_cambios_de_usuarios_en_auditoria_seguridad(admin):
    app = admin.application
    correo = crear_usuario(admin, rol="Cajero", password="Cajero1*")
    id_usuario = valor(app, "SELECT idUsuario FROM TblUsuarios WHERE correo = :c", c=correo)
    id_empleado = valor(app, "SELECT idEmpleado FROM TblUsuarios WHERE idUsuario = :u", u=id_usuario)
    id_rol_cajero = valor(app, "SELECT idRol FROM TblRoles WHERE nombre = 'Cajero'")
    id_rol_admin = valor(app, "SELECT idRol FROM TblRoles WHERE nombre = 'Administrador'")
    enviar(
        admin,
        "/usuarios/guardar",
        {
            "id_usuario": str(id_usuario),
            "correo": correo,
            "id_rol": str(id_rol_admin),
            "id_empleado": str(id_empleado),
            "activo": "1",
            "password": "Nueva1*Clave",
        },
    )
    filas = consulta(
        app,
        "SELECT accion, idRolAnterior, idRolNuevo, cambioPassword, idEmpleado "
        "FROM TblAuditoriaSeguridad WHERE tablaAfectada = 'TblUsuarios' AND idRegistro = :u "
        "ORDER BY idAuditoriaSeguridad",
        u=id_usuario,
    )
    id_admin = _id_empleado_admin(app)
    assert [tuple(fila) for fila in filas] == [
        ("INSERT", None, id_rol_cajero, True, id_admin),
        ("UPDATE", id_rol_cajero, id_rol_admin, True, id_admin),
    ]


def prueba_la_auditoria_nunca_guarda_el_hash_de_la_contrasena(app):
    columnas = {
        fila[0].lower()
        for fila in consulta(
            app,
            "SELECT c.name FROM sys.columns AS c "
            "JOIN sys.tables AS t ON t.object_id = c.object_id "
            "WHERE t.name LIKE 'auditoria%' OR t.name LIKE 'historial%'",
        )
    }
    assert not any("hash" in columna for columna in columnas)


def prueba_permisos_de_roles_en_auditoria_seguridad(admin):
    app = admin.application
    nombre = nombre_unico("Auditor")
    enviar(admin, "/roles/guardar", {"nombre": nombre, "permisos": ["caja.ver", "reportes.ver"]})
    id_rol = valor(app, "SELECT idRol FROM TblRoles WHERE nombre = :n", n=nombre)
    enviar(admin, "/roles/guardar", {"id_rol": str(id_rol), "nombre": nombre, "permisos": ["caja.ver"]})
    acciones = consulta(
        app,
        "SELECT accion, COUNT(*) FROM TblAuditoriaSeguridad "
        "WHERE tablaAfectada = 'TblRolesPermisos' AND idRegistro = :r GROUP BY accion",
        r=id_rol,
    )
    assert {fila[0]: fila[1] for fila in acciones} == {"INSERT": 2, "DELETE": 1}


def prueba_sesiones_exitosas_fallidas_y_cierres(app):
    correo_inexistente = "nadie.registrado@alma.com"
    cliente_http = app.test_client()
    enviar(cliente_http, "/validar_login", {"correo": correo_inexistente, "password": "x"})
    enviar(cliente_http, "/validar_login", {"correo": correo_inexistente, "password": "y"})
    iniciar_sesion(cliente_http, CORREO_ADMIN, PASSWORD_ADMIN)
    enviar(cliente_http, "/logout")
    eventos = consulta(
        app,
        "SELECT evento, correo, idEmpleado, direccionIp FROM TblAuditoriaSesiones "
        "WHERE correo IN (:c, 'admin@alma.com') ORDER BY idAuditoriaSesion",
        c=correo_inexistente,
    )
    assert [(fila.evento, fila.correo) for fila in eventos][-4:] == [
        ("LOGIN_FALLIDO", correo_inexistente),
        ("LOGIN_FALLIDO", correo_inexistente),
        ("LOGIN_OK", "admin@alma.com"),
        ("LOGOUT", "admin@alma.com"),
    ]
    assert eventos[-1].idEmpleado == _id_empleado_admin(app)
    assert eventos[-1].direccionIp == "127.0.0.1"
    assert valor(
        app,
        "SELECT intentosFallidos FROM vIntentosFallidosRecientes WHERE correo = :c",
        c=correo_inexistente,
    ) == 2


@pytest.mark.parametrize(
    ("tabla", "sentencia"),
    [
        ("TblHistorialProductos", "DELETE FROM TblHistorialProductos"),
        ("TblHistorialReservaciones", "UPDATE TblHistorialReservaciones SET estado = 'X'"),
        ("TblHistorialDetalleTicket", "DELETE FROM TblHistorialDetalleTicket"),
        ("TblAuditoriaCaja", "UPDATE TblAuditoriaCaja SET montoNuevo = 0"),
        ("TblAuditoriaSeguridad", "DELETE FROM TblAuditoriaSeguridad"),
        ("TblAuditoriaSesiones", "DELETE FROM TblAuditoriaSesiones"),
    ],
)
def prueba_la_auditoria_no_se_puede_alterar(app, tabla, sentencia):
    antes = valor(app, f"SELECT COUNT(*) FROM {tabla}")
    with pytest.raises(DBAPIError, match="no se pueden modificar ni eliminar"):
        _ejecutar(app, sentencia)
    assert valor(app, f"SELECT COUNT(*) FROM {tabla}") == antes


def prueba_desactivar_un_trigger_queda_registrado(app):
    try:
        _ejecutar(app, "ALTER TABLE TblPagos DISABLE TRIGGER trg_AuditoriaCajaPagosUpdate")
    finally:
        _ejecutar(app, "ALTER TABLE TblPagos ENABLE TRIGGER trg_AuditoriaCajaPagosUpdate")
    filas = consulta(
        app,
        "SELECT TOP 2 accion, detalle FROM TblAuditoriaSeguridad ORDER BY idAuditoriaSeguridad DESC",
    )
    assert {fila.accion for fila in filas} == {"ALTER_TABLE"}
    assert any("DISABLE TRIGGER" in fila.detalle for fila in filas)


def prueba_volver_a_migrar_no_cambia_nada(app):
    antes = valor(app, "SELECT COUNT(*) FROM TblAuditoriaSeguridad")
    assert migraciones.aplicar_migraciones(BASE_PRUEBAS) == {"adoptadas": [], "aplicadas": []}
    assert valor(app, "SELECT COUNT(*) FROM TblAuditoriaSeguridad") == antes


def prueba_pantalla_de_bitacoras_muestra_la_auditoria(admin):
    enviar(admin.application.test_client(), "/validar_login", {"correo": "x@alma.com", "password": "x"})
    html = texto(admin.get("/bitacoras"))
    for pestana in ("Productos", "Reservaciones", "Detalles de ticket", "Caja", "Seguridad", "Sesiones"):
        assert pestana in html
    assert "Intentos fallidos de inicio de sesión" in html
