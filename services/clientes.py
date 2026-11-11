from models import Cliente
from core.base_datos import db
from services.validaciones import validar_correo, validar_nombre, validar_telefono


def crear_cliente_sin_confirmar(*, nombre, telefono=None, correo=None, direccion=None):
    nombre = validar_nombre(nombre)
    telefono = validar_telefono(telefono)
    correo = validar_correo(correo) if (correo or "").strip() else None
    direccion = (direccion or "").strip() or None
    if direccion and len(direccion) > 350:
        raise ValueError("La dirección no puede superar 350 caracteres.")
    cliente = Cliente(
        nombre=nombre, telefono=telefono, email=correo, direccion=direccion
    )
    db.session.add(cliente)
    db.session.flush()
    return cliente


def guardar_cliente(id_cliente, *, nombre, telefono=None, correo=None, direccion=None):
    nombre = validar_nombre(nombre)
    telefono = validar_telefono(telefono)
    if correo:
        correo = validar_correo(correo)
    if direccion and len(direccion) > 350:
        raise ValueError("La dirección no puede superar 350 caracteres.")
    try:
        cliente = db.session.get(Cliente, id_cliente) if id_cliente else Cliente()
        if id_cliente and not cliente:
            raise LookupError("El cliente no existe.")
        cliente.nombre = nombre
        cliente.telefono = telefono
        cliente.email = correo or None
        cliente.direccion = direccion or None
        db.session.add(cliente)
        db.session.commit()
        return cliente
    except Exception:
        db.session.rollback()
        raise


def eliminar_cliente(id_cliente):
    try:
        cliente = db.session.get(Cliente, id_cliente)
        if not cliente:
            raise LookupError("El cliente no existe.")
        if cliente.reservaciones:
            raise ValueError("No se puede eliminar un cliente con reservaciones.")
        db.session.delete(cliente)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
