from core.base_datos import db


class Reservacion(db.Model):
    __tablename__ = "TblReservaciones"
    __table_args__ = {"implicit_returning": False}

    id_reservacion = db.Column("idReservacion", db.Integer, primary_key=True)
    id_cliente = db.Column(
        "idCliente",
        db.Integer,
        db.ForeignKey("TblClientes.idCliente"),
        nullable=False,
    )
    id_mesa = db.Column(
        "idMesa",
        db.Integer,
        db.ForeignKey("TblMesas.idMesa"),
        nullable=False,
    )
    id_empleado = db.Column(
        "idEmpleado",
        db.Integer,
        db.ForeignKey("TblEmpleados.idEmpleado"),
        nullable=False,
    )
    cantidad_personas = db.Column("cantidadPersonas", db.Integer, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora_reserva = db.Column("horaReserva", db.Time, nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="Confirmada")

    cliente = db.relationship("Cliente", back_populates="reservaciones")
    mesa = db.relationship("Mesa", back_populates="reservaciones")
    empleado = db.relationship("Empleado")
