from sqlalchemy import select

from models import Empleado, Permiso, Rol, Ticket, Usuario
from core.base_datos import db
from core.permisos import (
    MODULOS,
    PERMISOS,
    ROL_ADMINISTRADOR,
    accion_de,
    completar_dependencias,
    modulo_de,
)
from services.validaciones import validar_correo, validar_nombre_rol, validar_password


def _administradores_activos():
    return (
        Usuario.query.join(Rol)
        .filter(Rol.nombre == ROL_ADMINISTRADOR, Usuario.activo == True)
        .count()
    )


def _es_administrador(usuario):
    return bool(usuario and usuario.es_administrador)


def _codigos_de(usuario):
    if not usuario or not usuario.rol:
        return set()
    return usuario.rol.codigos


def _exigir_subconjunto(actor, codigos, mensaje):
    if _es_administrador(actor):
        return
    if not set(codigos) <= _codigos_de(actor):
        raise ValueError(mensaje)


def _validar_rol_asignable(actor, rol):
    if _es_administrador(actor):
        return
    if rol.es_administrador:
        raise ValueError("Solo un administrador puede asignar el rol Administrador.")
    _exigir_subconjunto(
        actor, rol.codigos, "No puede asignar un rol con permisos que usted no tiene."
    )


def _validar_usuario_gestionable(actor, usuario):
    if _es_administrador(actor) or not usuario.rol:
        return
    if usuario.es_administrador:
        raise ValueError("Solo un administrador puede modificar a otro administrador.")
    _exigir_subconjunto(
        actor,
        usuario.rol.codigos,
        "No puede modificar a un usuario que tiene permisos que usted no tiene.",
    )


def _validar_rol_gestionable(actor, rol):
    if _es_administrador(actor):
        return
    if actor and actor.id_rol == rol.id_rol:
        raise ValueError("No puede modificar los permisos de su propio rol.")
    _exigir_subconjunto(
        actor, rol.codigos, "No puede modificar un rol con permisos que usted no tiene."
    )


def _permisos_por_codigo(codigos):
    codigos = completar_dependencias(codigos)
    if not codigos:
        return []
    return (
        db.session.execute(select(Permiso).where(Permiso.codigo.in_(codigos)))
        .scalars()
        .all()
    )


def codigos_de_rol(id_rol):
    rol = db.session.get(Rol, id_rol)
    if not rol:
        raise LookupError("El rol base no existe.")
    if rol.es_administrador:
        return [codigo for codigo, _ in PERMISOS]
    return [permiso.codigo for permiso in rol.permisos]


def grupos_permisos(permisos):
    orden = list(MODULOS)
    grupos = {}
    for permiso in permisos:
        grupos.setdefault(modulo_de(permiso.codigo), []).append(permiso)
    resultado = []
    for modulo, lista in sorted(
        grupos.items(),
        key=lambda item: orden.index(item[0]) if item[0] in orden else len(orden),
    ):
        nombre, icono = MODULOS.get(modulo, (modulo.capitalize(), "bi-grid"))
        lista.sort(key=lambda p: (accion_de(p.codigo) != "ver", p.codigo))
        resultado.append(
            {"clave": modulo, "nombre": nombre, "icono": icono, "permisos": lista}
        )
    return resultado


def guardar_rol(id_rol, *, nombre, codigos_permisos, actor=None):
    nombre = validar_nombre_rol(nombre)
    try:
        rol = db.session.get(Rol, id_rol) if id_rol else Rol()
        if id_rol and not rol:
            raise LookupError("El rol no existe.")
        if rol.protegido and nombre != ROL_ADMINISTRADOR:
            raise ValueError("El rol Administrador no puede cambiar de nombre.")
        if not rol.protegido and nombre == ROL_ADMINISTRADOR:
            raise ValueError("Ese nombre está reservado para el rol Administrador.")
        if id_rol:
            _validar_rol_gestionable(actor, rol)

        rol.nombre = nombre
        if not rol.protegido:
            permisos = _permisos_por_codigo(codigos_permisos)
            _exigir_subconjunto(
                actor,
                {permiso.codigo for permiso in permisos},
                "No puede otorgar permisos que usted no tiene.",
            )
            rol.permisos = permisos
        db.session.add(rol)
        db.session.commit()
        return rol
    except Exception:
        db.session.rollback()
        raise


def renombrar_rol(id_rol, nombre, actor=None):
    nombre = validar_nombre_rol(nombre)
    try:
        rol = db.session.get(Rol, id_rol)
        if not rol:
            raise LookupError("El rol no existe.")
        if rol.protegido:
            raise ValueError("El rol Administrador no puede cambiar de nombre.")
        if nombre == ROL_ADMINISTRADOR:
            raise ValueError("Ese nombre está reservado para el rol Administrador.")
        _validar_rol_gestionable(actor, rol)
        rol.nombre = nombre
        db.session.commit()
        return rol
    except Exception:
        db.session.rollback()
        raise


def actualizar_permisos_rol(id_rol, codigos, actor=None):
    try:
        rol = db.session.get(Rol, id_rol)
        if not rol:
            raise LookupError("El rol no existe.")
        if rol.protegido:
            raise ValueError("El rol Administrador siempre tiene todos los permisos.")
        _validar_rol_gestionable(actor, rol)
        nuevos = _permisos_por_codigo(codigos)
        _exigir_subconjunto(
            actor,
            {permiso.codigo for permiso in nuevos},
            "No puede otorgar permisos que usted no tiene.",
        )
        cambio = {p.codigo for p in nuevos} != {p.codigo for p in rol.permisos}
        if cambio:
            rol.permisos = nuevos
        db.session.commit()
        return cambio
    except Exception:
        db.session.rollback()
        raise


def eliminar_rol(id_rol, actor=None):
    try:
        rol = db.session.get(Rol, id_rol)
        if not rol:
            raise LookupError("El rol no existe.")
        if rol.es_administrador:
            raise ValueError("El rol Administrador está protegido.")
        _validar_rol_gestionable(actor, rol)
        if rol.usuarios:
            raise ValueError("No se puede eliminar un rol que tiene usuarios.")
        db.session.delete(rol)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def guardar_usuario(
    id_usuario,
    *,
    correo,
    id_rol,
    id_empleado,
    activo,
    password=None,
    forzar_cambio_password=False,
    actor=None,
):
    correo = validar_correo(correo)
    if password:
        validar_password(password)
    try:
        usuario = db.session.get(Usuario, id_usuario) if id_usuario else Usuario()
        if id_usuario and not usuario:
            raise LookupError("El usuario no existe.")
        rol = db.session.get(Rol, id_rol) if id_rol else None
        empleado = db.session.get(Empleado, id_empleado) if id_empleado else None
        if not rol:
            raise ValueError("Seleccione un rol válido.")
        if not empleado or empleado.es_sistema or not empleado.activo:
            raise ValueError("Seleccione un empleado activo.")
        if id_usuario:
            _validar_usuario_gestionable(actor, usuario)
        _validar_rol_asignable(actor, rol)

        es_el_mismo = bool(id_usuario and actor and usuario.id_usuario == actor.id_usuario)
        if es_el_mismo and not activo:
            raise ValueError("No puede desactivar su propio usuario.")
        if es_el_mismo and rol.id_rol != usuario.id_rol and not _es_administrador(actor):
            raise ValueError("No puede cambiar su propio rol.")

        otro_usuario = Usuario.query.filter(
            Usuario.id_empleado == id_empleado,
            Usuario.id_usuario != (id_usuario or 0),
        ).first()
        if otro_usuario:
            raise ValueError("El empleado ya tiene un usuario asociado.")
        if not id_usuario and not password:
            raise ValueError("La contraseña es obligatoria para un usuario nuevo.")
        if id_usuario and usuario.es_administrador:
            quita_administracion = not activo or not rol.es_administrador
            if quita_administracion and _administradores_activos() <= 1:
                raise ValueError("Debe existir al menos un administrador activo.")

        usuario.correo = correo
        usuario.id_rol = rol.id_rol
        usuario.id_empleado = empleado.id_empleado
        usuario.activo = activo
        usuario.debe_cambiar_password = forzar_cambio_password
        if password:
            usuario.asignar_password(password)
        db.session.add(usuario)
        db.session.commit()
        return usuario
    except Exception:
        db.session.rollback()
        raise


def eliminar_usuario(id_usuario, actor=None):
    try:
        usuario = db.session.get(Usuario, id_usuario)
        if not usuario:
            raise LookupError("El usuario no existe.")
        if actor and usuario.id_usuario == actor.id_usuario:
            raise ValueError("No puede eliminar su propio usuario.")
        _validar_usuario_gestionable(actor, usuario)
        if (
            usuario.es_administrador
            and usuario.activo
            and _administradores_activos() <= 1
        ):
            raise ValueError("Debe existir al menos un administrador activo.")

        if Ticket.query.filter_by(id_usuario=usuario.id_usuario).first():
            usuario.activo = False
        else:
            db.session.delete(usuario)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def cambiar_password(usuario, password_actual, password_nueva):
    if not usuario.verificar_password(password_actual):
        raise ValueError("La contraseña actual es incorrecta.")
    if password_actual == password_nueva:
        raise ValueError("La nueva contraseña debe ser distinta de la actual.")
    validar_password(password_nueva)
    try:
        usuario.asignar_password(password_nueva)
        usuario.debe_cambiar_password = False
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
