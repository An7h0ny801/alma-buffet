from flask import g, has_app_context
from sqlalchemy import event, text
from sqlalchemy.orm import Session


CLAVE_EMPLEADO = "idEmpleado"

_ASIGNAR_EMPLEADO = text(
    "EXEC sp_set_session_context @key = :clave, @value = :id_empleado"
)


def id_empleado_actual():
    if not has_app_context() or not g.get("usuario"):
        return None
    return g.get("id_empleado")


def _asignar_empleado_a_conexion(sesion, transaccion, conexion):
    if conexion.dialect.name != "mssql":
        return
    conexion.execute(
        _ASIGNAR_EMPLEADO,
        {"clave": CLAVE_EMPLEADO, "id_empleado": id_empleado_actual()},
    )


def asignar_empleado_en_transaccion(sesion):
    _asignar_empleado_a_conexion(sesion, None, sesion.connection())


def registrar_contexto_empleado():
    if not event.contains(Session, "after_begin", _asignar_empleado_a_conexion):
        event.listen(Session, "after_begin", _asignar_empleado_a_conexion)
