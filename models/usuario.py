from core.base_datos import db
from core.contrasenas import generar_hash, necesita_actualizarse, verificar_hash


class Usuario(db.Model):
    __tablename__ = "TblUsuarios"
    __table_args__ = {"implicit_returning": False}

    id_usuario = db.Column("idUsuario", db.Integer, primary_key=True)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column("passwordHash", db.String(255), nullable=False)
    id_rol = db.Column(
        "idRol", db.Integer, db.ForeignKey("TblRoles.idRol"), nullable=False
    )
    id_empleado = db.Column(
        "idEmpleado",
        db.Integer,
        db.ForeignKey("TblEmpleados.idEmpleado"),
        nullable=False,
        unique=True,
    )
    activo = db.Column(db.Boolean, nullable=False, default=True)
    debe_cambiar_password = db.Column(
        "debeCambiarPassword", db.Boolean, nullable=False, default=False
    )

    rol = db.relationship("Rol", back_populates="usuarios")
    empleado = db.relationship("Empleado", back_populates="usuario")

    def asignar_password(self, password):
        self.password_hash = generar_hash(password)

    def verificar_password(self, password):
        return verificar_hash(self.password_hash, password)

    @property
    def hash_desactualizado(self):
        return necesita_actualizarse(self.password_hash)

    @property
    def nombre(self):
        return self.empleado.nombre if self.empleado else self.correo

    @property
    def es_administrador(self):
        return bool(self.rol and self.rol.es_administrador)

    def tiene_permiso(self, codigo):
        return bool(self.activo and self.rol and self.rol.tiene_permiso(codigo))
