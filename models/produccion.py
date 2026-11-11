from datetime import datetime

from core.base_datos import db


class Produccion(db.Model):
    __tablename__ = "TblProduccion"

    id_produccion = db.Column("idTblProduccion", db.Integer, primary_key=True)
    id_producto = db.Column(
        "idProducto",
        db.Integer,
        db.ForeignKey("TblProductos.idProducto"),
        nullable=False,
    )
    id_empleado = db.Column(
        "idEmpleado",
        db.Integer,
        db.ForeignKey("TblEmpleados.idEmpleado"),
        nullable=False,
    )
    fecha = db.Column(db.Date, nullable=False, default=lambda: datetime.now().date())
    hora = db.Column(db.Time, nullable=False, default=lambda: datetime.now().time())
    cantidad_producida_unidades = db.Column(
        "cantidadProducidaUnidades", db.Integer, nullable=False
    )

    producto = db.relationship("Producto", back_populates="producciones")
    empleado = db.relationship("Empleado")
