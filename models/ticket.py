from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from core.base_datos import db


CENTIMO = Decimal("0.01")


class Ticket(db.Model):
    __tablename__ = "TblTickets"
    __table_args__ = {"implicit_returning": False}

    id_ticket = db.Column("idTicket", db.Integer, primary_key=True)
    id_mesa = db.Column(
        "idMesa",
        db.Integer,
        db.ForeignKey("TblMesas.idMesa"),
        nullable=True,
    )
    id_usuario = db.Column(
        "idUsuario",
        db.Integer,
        db.ForeignKey("TblUsuarios.idUsuario"),
        nullable=False,
    )
    fecha = db.Column(db.Date, nullable=False, default=lambda: datetime.now().date())
    hora_inicio = db.Column(
        "horaInicio", db.Time, nullable=False, default=lambda: datetime.now().time()
    )
    fecha_hora_fin = db.Column("fechaHoraFin", db.DateTime, nullable=True)
    estado = db.Column(db.String(20), nullable=False, default="Pendiente")

    mesa = db.relationship("Mesa", back_populates="tickets")
    usuario = db.relationship("Usuario")
    detalles = db.relationship(
        "DetalleTicket",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )
    pago = db.relationship("Pago", back_populates="ticket", uselist=False)

    @property
    def subtotal(self):
        return sum((detalle.subtotal for detalle in self.detalles), Decimal("0.00"))

    @property
    def impuesto(self):
        return (self.subtotal * Decimal("0.13")).quantize(CENTIMO, rounding=ROUND_HALF_UP)

    @property
    def total(self):
        return (self.subtotal * Decimal("1.13")).quantize(CENTIMO, rounding=ROUND_HALF_UP)

    @property
    def modalidad(self):
        return "En el local" if self.id_mesa else "Para llevar"
