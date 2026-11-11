from datetime import datetime

from core.base_datos import db


class ContextoAuditoria:
    usuario_bd = db.Column("usuarioBD", db.Unicode(128))
    equipo = db.Column(db.Unicode(128))
    aplicacion = db.Column(db.Unicode(128))


class HistorialProducto(ContextoAuditoria, db.Model):
    __tablename__ = "TblHistorialProductos"

    id_historial_producto = db.Column(
        "idHistorialProducto", db.Integer, primary_key=True
    )
    id_producto = db.Column("idProducto", db.Integer)
    id_empleado = db.Column("idEmpleado", db.Integer, nullable=False)
    fecha_cambio = db.Column(
        "fechaCambio", db.DateTime, nullable=False, default=datetime.now
    )
    accion = db.Column(db.String(10), nullable=False)
    nombre = db.Column(db.String(100))
    precio_unidad = db.Column("precioUnidad", db.Numeric(10, 2))
    unidad_medida = db.Column("unidadMedida", db.String(20))
    stock_unidades = db.Column("stockUnidades", db.Integer)
    activo = db.Column(db.Boolean)
    nombre_anterior = db.Column("nombreAnterior", db.String(100))
    precio_unidad_anterior = db.Column("precioUnidadAnterior", db.Numeric(10, 2))
    unidad_medida_anterior = db.Column("unidadMedidaAnterior", db.String(20))
    stock_unidades_anterior = db.Column("stockUnidadesAnterior", db.Integer)
    activo_anterior = db.Column("activoAnterior", db.Boolean)


class HistorialReservacion(ContextoAuditoria, db.Model):
    __tablename__ = "TblHistorialReservaciones"

    id_historial_reservacion = db.Column(
        "idHistorialReservacion", db.Integer, primary_key=True
    )
    id_reservacion = db.Column("idReservacion", db.Integer)
    id_empleado = db.Column("idEmpleado", db.Integer, nullable=False)
    id_cliente = db.Column("idCliente", db.Integer)
    id_mesa = db.Column("idMesa", db.Integer)
    fecha = db.Column(db.Date)
    fecha_cambio = db.Column(
        "fechaCambio", db.DateTime, nullable=False, default=datetime.now
    )
    hora_reserva = db.Column("horaReserva", db.Time)
    accion = db.Column(db.String(10), nullable=False)
    cantidad_personas = db.Column("cantidadPersonas", db.Integer)
    estado = db.Column(db.String(20))
    id_cliente_anterior = db.Column("idClienteAnterior", db.Integer)
    id_mesa_anterior = db.Column("idMesaAnterior", db.Integer)
    fecha_anterior = db.Column("fechaAnterior", db.Date)
    hora_reserva_anterior = db.Column("horaReservaAnterior", db.Time)
    cantidad_personas_anterior = db.Column("cantidadPersonasAnterior", db.Integer)
    estado_anterior = db.Column("estadoAnterior", db.String(20))


class HistorialDetalleTicket(ContextoAuditoria, db.Model):
    __tablename__ = "TblHistorialDetalleTicket"

    id_historial_detalle = db.Column(
        "idHistorialDetalle", db.Integer, primary_key=True
    )
    id_detalle = db.Column("idDetalle", db.Integer)
    id_ticket = db.Column("idTicket", db.Integer)
    id_producto = db.Column("idProducto", db.Integer)
    id_empleado = db.Column("idEmpleado", db.Integer, nullable=False)
    fecha_cambio = db.Column(
        "fechaCambio", db.DateTime, nullable=False, default=datetime.now
    )
    accion = db.Column(db.String(10), nullable=False)
    cantidad_unidades = db.Column("cantidadUnidades", db.Integer)
    precio_unidad = db.Column("precioUnidad", db.Numeric(10, 2))
    subtotal = db.Column(db.Numeric(10, 2))
    cantidad_unidades_anterior = db.Column("cantidadUnidadesAnterior", db.Integer)
    precio_unidad_anterior = db.Column("precioUnidadAnterior", db.Numeric(10, 2))
    subtotal_anterior = db.Column("subtotalAnterior", db.Numeric(10, 2))


class AuditoriaCaja(ContextoAuditoria, db.Model):
    __tablename__ = "TblAuditoriaCaja"

    id_auditoria_caja = db.Column("idAuditoriaCaja", db.Integer, primary_key=True)
    fecha_hora = db.Column("fechaHora", db.DateTime, nullable=False)
    id_empleado = db.Column("idEmpleado", db.Integer, nullable=False)
    tabla_afectada = db.Column("tablaAfectada", db.String(30), nullable=False)
    accion = db.Column(db.String(10), nullable=False)
    id_registro = db.Column("idRegistro", db.Integer, nullable=False)
    id_ticket = db.Column("idTicket", db.Integer)
    monto_ticket = db.Column("montoTicket", db.Numeric(10, 2))
    estado_anterior = db.Column("estadoAnterior", db.String(20))
    estado_nuevo = db.Column("estadoNuevo", db.String(20))
    monto_anterior = db.Column("montoAnterior", db.Numeric(10, 2))
    monto_nuevo = db.Column("montoNuevo", db.Numeric(10, 2))
    metodo_pago_anterior = db.Column("metodoPagoAnterior", db.String(20))
    metodo_pago_nuevo = db.Column("metodoPagoNuevo", db.String(20))
    referencia_anterior = db.Column("referenciaAnterior", db.String(60))
    referencia_nueva = db.Column("referenciaNueva", db.String(60))


class AuditoriaSeguridad(ContextoAuditoria, db.Model):
    __tablename__ = "TblAuditoriaSeguridad"

    id_auditoria_seguridad = db.Column(
        "idAuditoriaSeguridad", db.Integer, primary_key=True
    )
    fecha_hora = db.Column("fechaHora", db.DateTime, nullable=False)
    id_empleado = db.Column("idEmpleado", db.Integer, nullable=False)
    tabla_afectada = db.Column("tablaAfectada", db.Unicode(128), nullable=False)
    accion = db.Column(db.String(40), nullable=False)
    id_registro = db.Column("idRegistro", db.Integer)
    correo_anterior = db.Column("correoAnterior", db.String(120))
    correo_nuevo = db.Column("correoNuevo", db.String(120))
    id_rol_anterior = db.Column("idRolAnterior", db.Integer)
    id_rol_nuevo = db.Column("idRolNuevo", db.Integer)
    activo_anterior = db.Column("activoAnterior", db.Boolean)
    activo_nuevo = db.Column("activoNuevo", db.Boolean)
    cambio_password = db.Column("cambioPassword", db.Boolean)
    id_permiso = db.Column("idPermiso", db.Integer)
    detalle = db.Column(db.UnicodeText)


class AuditoriaSesion(db.Model):
    __tablename__ = "TblAuditoriaSesiones"

    id_auditoria_sesion = db.Column("idAuditoriaSesion", db.Integer, primary_key=True)
    fecha_hora = db.Column("fechaHora", db.DateTime, nullable=False)
    evento = db.Column(db.String(20), nullable=False)
    correo = db.Column(db.String(120), nullable=False)
    id_usuario = db.Column("idUsuario", db.Integer)
    id_empleado = db.Column("idEmpleado", db.Integer)
    direccion_ip = db.Column("direccionIp", db.String(45))
    navegador = db.Column(db.String(200))
    usuario_bd = db.Column("usuarioBD", db.Unicode(128))
    equipo = db.Column(db.Unicode(128))
