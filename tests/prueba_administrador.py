import pytest

from core import migraciones
from core.administrador import (
    AdministradorExistente,
    existe_administrador,
    inicializar_administrador,
    restablecer_administrador,
)
from core.configuracion import url_base_datos
from tests.conftest import CONFIGURACION_PRUEBAS, preparar_base
from tests.utilidades import CORREO_ADMIN, consulta, iniciar_sesion, texto, valor


BASE_LIMPIA = "BUFFET_ALMA_PRUEBAS_LIMPIA"


@pytest.fixture(scope="module")
def app_limpia():
    preparar_base(BASE_LIMPIA, con_demostracion=False)
    from core.aplicacion import crear_app
    from core.base_datos import db

    aplicacion = crear_app(
        {**CONFIGURACION_PRUEBAS, "SQLALCHEMY_DATABASE_URI": url_base_datos(BASE_LIMPIA)}
    )
    yield aplicacion
    with aplicacion.app_context():
        db.session.remove()
        db.engine.dispose()
    migraciones.eliminar_base(BASE_LIMPIA)


def _invocar(aplicacion, argumentos, **entorno):
    variables = {"ADMIN_CORREO": "", "ADMIN_PASSWORD": "", "ADMIN_NOMBRE": ""}
    variables.update(entorno)
    return aplicacion.test_cli_runner().invoke(args=argumentos, env=variables)


def prueba_instalacion_limpia_no_trae_usuarios(app_limpia):
    assert valor(app_limpia, "SELECT COUNT(*) FROM TblUsuarios") == 0
    assert valor(app_limpia, "SELECT COUNT(*) FROM TblPermisos") == 22
    assert valor(app_limpia, "SELECT COUNT(*) FROM TblRoles") == 4
    assert valor(app_limpia, "SELECT COUNT(*) FROM TblEmpleados WHERE esSistema = 1") == 1
    assert valor(app_limpia, "SELECT COUNT(*) FROM TblEmpleados WHERE esSistema = 0") == 0
    with app_limpia.app_context():
        assert not existe_administrador()
    assert app_limpia.test_client().get("/login").status_code == 200


def prueba_sin_datos_el_comando_no_crea_nada(app_limpia):
    resultado = _invocar(app_limpia, ["inicializar-admin"])
    assert resultado.exit_code == 1
    assert "ADMIN_CORREO" in resultado.output
    resultado = _invocar(app_limpia, ["inicializar-admin", "--si-falta"])
    assert resultado.exit_code == 0
    assert valor(app_limpia, "SELECT COUNT(*) FROM TblUsuarios") == 0


def prueba_contrasena_debil_es_rechazada(app_limpia):
    resultado = _invocar(
        app_limpia, ["inicializar-admin"], ADMIN_CORREO="jefe@alma.com", ADMIN_PASSWORD="debil"
    )
    assert resultado.exit_code == 1
    assert valor(app_limpia, "SELECT COUNT(*) FROM TblUsuarios") == 0


def prueba_primer_administrador_desde_variables_de_entorno(app_limpia):
    resultado = _invocar(
        app_limpia,
        ["inicializar-admin"],
        ADMIN_CORREO="Jefe@Alma.com",
        ADMIN_PASSWORD="Inicial1*Segura",
        ADMIN_NOMBRE="Jefa General",
    )
    assert resultado.exit_code == 0, resultado.output
    assert "Administrador creado: jefe@alma.com" in resultado.output
    fila = consulta(
        app_limpia,
        "SELECT u.passwordHash, u.debeCambiarPassword, r.nombre AS rol, e.nombre "
        "FROM TblUsuarios u JOIN TblRoles r ON r.idRol = u.idRol "
        "JOIN TblEmpleados e ON e.idEmpleado = u.idEmpleado WHERE u.correo = 'jefe@alma.com'",
    )[0]
    assert fila.passwordHash.startswith("$argon2id$")
    assert fila.debeCambiarPassword is True
    assert (fila.rol, fila.nombre) == ("Administrador", "Jefa General")

    cliente_http = app_limpia.test_client()
    respuesta = iniciar_sesion(cliente_http, "jefe@alma.com", "Inicial1*Segura")
    assert "/cambiar-password" in respuesta.location
    assert "/cambiar-password" in cliente_http.get("/usuarios").location


def prueba_la_inicializacion_no_se_repite_ni_sobrescribe(app_limpia):
    resultado = _invocar(
        app_limpia, ["inicializar-admin"], ADMIN_CORREO="otro@alma.com", ADMIN_PASSWORD="Otra1*Segura"
    )
    assert resultado.exit_code == 0
    assert "Ya existe un administrador" in resultado.output
    assert "elimine ADMIN_PASSWORD" in resultado.output
    assert valor(app_limpia, "SELECT COUNT(*) FROM TblUsuarios") == 1
    with app_limpia.app_context():
        with pytest.raises(AdministradorExistente):
            inicializar_administrador("tercero@alma.com", "Tercera1*Segura")
    assert valor(app_limpia, "SELECT COUNT(*) FROM TblUsuarios") == 1
    assert "/cambiar-password" in iniciar_sesion(
        app_limpia.test_client(), "jefe@alma.com", "Inicial1*Segura"
    ).location


def prueba_restablecer_solo_funciona_en_consola(app_limpia):
    resultado = _invocar(app_limpia, ["restablecer-admin", "--correo", "jefe@alma.com"])
    assert resultado.exit_code == 1
    assert "consola interactiva" in resultado.output
    resultado = _invocar(app_limpia, ["crear-usuario-bd"])
    assert resultado.exit_code == 1


def prueba_restablecer_administrador(app, admin):
    with app.app_context():
        with pytest.raises(ValueError, match="No existe un administrador"):
            restablecer_administrador("luz@alma.com", "Segura1*Admin")
        with pytest.raises(ValueError):
            restablecer_administrador(CORREO_ADMIN, "debil")


def prueba_no_existe_formulario_para_crear_administradores_sin_sesion(cliente):
    assert "/login" in cliente.get("/usuarios").location
    assert "Administrador" not in texto(cliente.get("/login"))
