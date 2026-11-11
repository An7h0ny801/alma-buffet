from core.base_datos import db


roles_permisos = db.Table(
    "TblRolesPermisos",
    db.Column(
        "idRol",
        db.Integer,
        db.ForeignKey("TblRoles.idRol", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "idPermiso",
        db.Integer,
        db.ForeignKey("TblPermisos.idPermiso", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Permiso(db.Model):
    __tablename__ = "TblPermisos"

    id_permiso = db.Column("idPermiso", db.Integer, primary_key=True)
    codigo = db.Column(db.String(60), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)

    roles = db.relationship(
        "Rol",
        secondary=roles_permisos,
        back_populates="permisos",
    )

    def __repr__(self):
        return self.nombre
