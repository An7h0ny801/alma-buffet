from core.base_datos import db


class Mesa(db.Model):
    __tablename__ = "TblMesas"

    id_mesa = db.Column("idMesa", db.Integer, primary_key=True)
    numero_mesa = db.Column("numeroMesa", db.Integer, unique=True, nullable=False)
    capacidad = db.Column(db.Integer, nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)

    tickets = db.relationship("Ticket", back_populates="mesa")
    reservaciones = db.relationship("Reservacion", back_populates="mesa")

    def __repr__(self):
        return f"Mesa {self.numero_mesa}"
