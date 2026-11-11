from core.base_datos import db


class Empleado(db.Model):
    __tablename__ = "TblEmpleados"

    id_empleado = db.Column("idEmpleado", db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    puesto = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(8))
    fecha_contratacion = db.Column("fechaContratacion", db.Date, nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    es_sistema = db.Column("esSistema", db.Boolean, nullable=False, default=False)

    usuario = db.relationship("Usuario", back_populates="empleado", uselist=False)

    def __repr__(self):
        return self.nombre
