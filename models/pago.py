from datetime import datetime

from core.base_datos import db


class Pago(db.Model):
    __tablename__ = "TblPagos"
    __table_args__ = {"implicit_returning": False}

    id_pago = db.Column("idPago", db.Integer, primary_key=True)
    id_ticket = db.Column(
        "idTicket",
        db.Integer,
        db.ForeignKey("TblTickets.idTicket"),
        unique=True,
        nullable=False,
    )
    monto_total = db.Column("montoTotal", db.Numeric(10, 2), nullable=False)
    metodo_pago = db.Column("metodoPago", db.String(20), nullable=False)
    fecha = db.Column(db.Date, nullable=False, default=lambda: datetime.now().date())
    hora = db.Column(db.Time, nullable=False, default=lambda: datetime.now().time())
    referencia = db.Column(db.String(60))

    ticket = db.relationship("Ticket", back_populates="pago")
