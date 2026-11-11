from datetime import date

from sqlalchemy import text

from core.base_datos import db
from core.permisos import ROL_ADMINISTRADOR
from models import Empleado, Rol, Usuario
from services.validaciones import validar_correo, validar_nombre, validar_password


NOMBRE_PREDETERMINADO = "Administrador General"
RECURSO_BLOQUEO = "AlmaBuffet.InicializarAdministrador"


class AdministradorExistente(RuntimeError):
    pass


def _rol_administrador():
    rol = Rol.query.filter_by(nombre=ROL_ADMINISTRADOR).first()
    if not rol:
        raise LookupError("No existe el rol Administrador. Ejecute primero las migraciones.")
    return rol


def existe_administrador():
    return (
        Usuario.query.join(Rol).filter(Rol.nombre == ROL_ADMINISTRADOR).first() is not None
    )


def inicializar_administrador(correo, password, nombre=None, debe_cambiar_password=False):
    correo = validar_correo(correo)
    validar_password(password)
    nombre = validar_nombre(nombre or NOMBRE_PREDETERMINADO)
    try:
        db.session.execute(
            text(
                "EXEC sp_getapplock @Resource = :recurso, @LockMode = 'Exclusive', "
                "@LockOwner = 'Transaction', @LockTimeout = 30000"
            ),
            {"recurso": RECURSO_BLOQUEO},
        )
        if existe_administrador():
            raise AdministradorExistente(
                "Ya existe un administrador. La inicialización solo puede ejecutarse una vez."
            )
        if Usuario.query.filter_by(correo=correo).first():
            raise ValueError("Ese correo ya pertenece a otro usuario.")
        empleado = Empleado(
            nombre=nombre,
            puesto="Administrador",
            fecha_contratacion=date.today(),
            activo=True,
            es_sistema=False,
        )
        usuario = Usuario(
            correo=correo,
            rol=_rol_administrador(),
            empleado=empleado,
            activo=True,
            debe_cambiar_password=debe_cambiar_password,
        )
        usuario.asignar_password(password)
        db.session.add_all([empleado, usuario])
        db.session.commit()
        return usuario
    except Exception:
        db.session.rollback()
        raise


def restablecer_administrador(correo, password):
    correo = validar_correo(correo)
    validar_password(password)
    try:
        usuario = Usuario.query.filter_by(correo=correo).first()
        if not usuario or not usuario.es_administrador:
            raise ValueError("No existe un administrador con ese correo.")
        usuario.asignar_password(password)
        usuario.activo = True
        usuario.debe_cambiar_password = False
        usuario.empleado.activo = True
        db.session.commit()
        return usuario
    except Exception:
        db.session.rollback()
        raise
