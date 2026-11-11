import os
import sys
from pathlib import Path

import pytest
from jinja2 import StrictUndefined


RAIZ = Path(__file__).resolve().parent.parent
BASE_PRUEBAS = "BUFFET_ALMA_PRUEBAS_AUTO"
DATOS_DEMOSTRACION = RAIZ / "tests" / "datos" / "datos_demostracion.sql"

sys.path.insert(0, str(RAIZ))

os.environ["APP_ENV"] = "pruebas"
os.environ["DB_NAME"] = BASE_PRUEBAS
os.environ["DB_HOST"] = os.getenv("PRUEBAS_DB_HOST", "")
os.environ["DB_USER"] = os.getenv("PRUEBAS_DB_USER", "")
os.environ["DB_PASSWORD"] = os.getenv("PRUEBAS_DB_PASSWORD", "")
for variable in (
    "DB_MIGRACION_USER",
    "DB_MIGRACION_PASSWORD",
    "ADMIN_CORREO",
    "ADMIN_PASSWORD",
    "ADMIN_NOMBRE",
    "SECRET_KEY",
    "ZONA_HORARIA_BD",
    "FLASK_DEBUG",
):
    os.environ[variable] = ""

from core import migraciones
from tests.utilidades import CORREO_ADMIN, PASSWORD_ADMIN, iniciar_sesion


CONFIGURACION_PRUEBAS = {
    "TESTING": True,
    "LOGIN_MAX_INTENTOS_IP": 100000,
}


def preparar_base(nombre, con_demostracion=True):
    migraciones.eliminar_base(nombre)
    migraciones.crear_base_si_falta(nombre)
    migraciones.aplicar_migraciones(nombre)
    if con_demostracion:
        migraciones.cargar_script(DATOS_DEMOSTRACION, nombre)


@pytest.fixture(scope="session")
def app():
    preparar_base(BASE_PRUEBAS)
    from core.administrador import restablecer_administrador
    from core.aplicacion import crear_app
    from core.base_datos import db

    aplicacion = crear_app(CONFIGURACION_PRUEBAS)
    aplicacion.jinja_env.undefined = StrictUndefined
    with aplicacion.app_context():
        restablecer_administrador(CORREO_ADMIN, PASSWORD_ADMIN)
    yield aplicacion
    with aplicacion.app_context():
        db.session.remove()
        db.engine.dispose()
    migraciones.eliminar_base(BASE_PRUEBAS)


@pytest.fixture()
def cliente(app):
    return app.test_client()


@pytest.fixture()
def admin(app):
    cliente_http = app.test_client()
    iniciar_sesion(cliente_http, CORREO_ADMIN, PASSWORD_ADMIN)
    return cliente_http
