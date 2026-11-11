from core.base_datos import db


class Producto(db.Model):
    __tablename__ = "TblProductos"
    __table_args__ = {"implicit_returning": False}

    id_producto = db.Column("idProducto", db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio_unidad = db.Column("precioUnidad", db.Numeric(10, 2), nullable=False)
    unidad_medida = db.Column("unidadMedida", db.String(20), nullable=False)
    stock_unidades = db.Column(
        "stockUnidades", db.Integer, nullable=False, default=0
    )
    activo = db.Column(db.Boolean, nullable=False, default=True)

    detalles = db.relationship("DetalleTicket", back_populates="producto")
    producciones = db.relationship("Produccion", back_populates="producto")

    @property
    def es_fresco_gratuito(self):
        return self.unidad_medida == "Vaso" and float(self.precio_unidad) == 0

    def __repr__(self):
        return self.nombre
