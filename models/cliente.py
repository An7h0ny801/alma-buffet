from datetime import datetime

from core.base_datos import db


class Cliente(db.Model):
    __tablename__ = "TblClientes"

    id_cliente = db.Column("idCliente", db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(8))
    email = db.Column(db.String(120))
    direccion = db.Column(db.String(350))
    fecha_registro = db.Column(
        "fechaRegistro", db.DateTime, nullable=False, default=datetime.now
    )

    reservaciones = db.relationship("Reservacion", back_populates="cliente")

    def __repr__(self):
        return self.nombre
