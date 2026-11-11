from core.base_datos import db
from core.permisos import PERMISOS, ROL_ADMINISTRADOR
from models.permiso import roles_permisos


class Rol(db.Model):
    __tablename__ = "TblRoles"

    id_rol = db.Column("idRol", db.Integer, primary_key=True)
    nombre = db.Column(db.String(30), unique=True, nullable=False)
    protegido = db.Column(db.Boolean, nullable=False, default=False)

    usuarios = db.relationship("Usuario", back_populates="rol")
    permisos = db.relationship(
        "Permiso",
        secondary=roles_permisos,
        back_populates="roles",
    )

    @property
    def es_administrador(self):
        return bool(self.protegido or self.nombre == ROL_ADMINISTRADOR)

    @property
    def codigos(self):
        if self.es_administrador:
            return {codigo for codigo, _ in PERMISOS}
        return {permiso.codigo for permiso in self.permisos}

    def tiene_permiso(self, codigo):
        return codigo in self.codigos

    def __repr__(self):
        return self.nombre
