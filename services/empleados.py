from models import (
    Empleado,
    HistorialDetalleTicket,
    HistorialProducto,
    HistorialReservacion,
    Produccion,
    Reservacion,
)
from core.base_datos import db
from services.validaciones import validar_nombre, validar_telefono


def guardar_empleado(
    id_empleado,
    *,
    nombre,
    puesto,
    telefono,
    fecha_contratacion,
    activo,
):
    nombre = validar_nombre(nombre)
    puesto = validar_nombre(puesto, "El puesto")
    telefono = validar_telefono(telefono)
    try:
        empleado = db.session.get(Empleado, id_empleado) if id_empleado else Empleado()
        if id_empleado and not empleado:
            raise LookupError("El empleado no existe.")
        if empleado.es_sistema:
            raise ValueError("El empleado técnico Sistema está protegido.")
        empleado.nombre = nombre
        empleado.puesto = puesto
        empleado.telefono = telefono
        empleado.fecha_contratacion = fecha_contratacion
        empleado.activo = activo
        if not activo and empleado.usuario:
            empleado.usuario.activo = False
        db.session.add(empleado)
        db.session.commit()
        return empleado
    except Exception:
        db.session.rollback()
        raise


def eliminar_empleado(id_empleado, id_empleado_actual=None):
    try:
        empleado = db.session.get(Empleado, id_empleado)
        if not empleado:
            raise LookupError("El empleado no existe.")
        if empleado.es_sistema:
            raise ValueError("El empleado técnico Sistema está protegido.")
        if empleado.id_empleado == id_empleado_actual:
            raise ValueError("No puede eliminar su propio registro de empleado.")
        tiene_historial = bool(
            empleado.usuario
            or Reservacion.query.filter_by(id_empleado=id_empleado).first()
            or Produccion.query.filter_by(id_empleado=id_empleado).first()
            or HistorialProducto.query.filter_by(id_empleado=id_empleado).first()
            or HistorialReservacion.query.filter_by(id_empleado=id_empleado).first()
            or HistorialDetalleTicket.query.filter_by(id_empleado=id_empleado).first()
        )
        if tiene_historial:
            empleado.activo = False
            if empleado.usuario:
                empleado.usuario.activo = False
            resultado = "archivado"
        else:
            db.session.delete(empleado)
            resultado = "eliminado"
        db.session.commit()
        return resultado
    except Exception:
        db.session.rollback()
        raise
