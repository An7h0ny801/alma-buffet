from core.base_datos import db


class DetalleTicket(db.Model):
    __tablename__ = "TblDetalleTicket"
    __table_args__ = {"implicit_returning": False}

    id_detalle = db.Column("idDetalle", db.Integer, primary_key=True)
    id_ticket = db.Column(
        "idTicket",
        db.Integer,
        db.ForeignKey("TblTickets.idTicket", ondelete="CASCADE"),
        nullable=False,
    )
    id_producto = db.Column(
        "idProducto",
        db.Integer,
        db.ForeignKey("TblProductos.idProducto"),
        nullable=False,
    )
    cantidad_unidades = db.Column("cantidadUnidades", db.Integer, nullable=False)
    precio_unidad = db.Column("precioUnidad", db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

    ticket = db.relationship("Ticket", back_populates="detalles")
    producto = db.relationship("Producto", back_populates="detalles")
