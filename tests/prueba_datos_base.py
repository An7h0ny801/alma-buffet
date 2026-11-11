from core.permisos import PERMISOS, ROLES_BASE
from tests.utilidades import consulta


def prueba_permisos_de_la_base_coinciden_con_el_catalogo(app):
    filas = consulta(app, "SELECT idPermiso, codigo, nombre FROM TblPermisos ORDER BY idPermiso")
    esperado = [(indice + 1, codigo, nombre) for indice, (codigo, nombre) in enumerate(PERMISOS)]
    assert [tuple(fila) for fila in filas] == esperado


def prueba_roles_base_tienen_sus_permisos(app):
    for rol, codigos in ROLES_BASE.items():
        asignados = {
            fila[0]
            for fila in consulta(
                app,
                "SELECT p.codigo FROM TblRolesPermisos rp "
                "JOIN TblPermisos p ON p.idPermiso = rp.idPermiso "
                "JOIN TblRoles r ON r.idRol = rp.idRol WHERE r.nombre = :rol",
                rol=rol,
            )
        }
        assert asignados == set(codigos or [codigo for codigo, _ in PERMISOS]), rol
