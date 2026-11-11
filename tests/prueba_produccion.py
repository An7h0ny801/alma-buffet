from datetime import datetime

import pytest
from flask import request
from sqlalchemy.pool import NullPool

from core.configuracion import ConfiguracionInvalida, cargar_configuracion


VARIABLES_PRODUCCION = {
    "APP_ENV": "produccion",
    "SECRET_KEY": "k" * 48,
    "DB_HOST": "servidor-de-prueba.database.windows.net",
    "DB_PORT": "1433",
    "DB_NAME": "BUFFET_ALMA",
    "DB_USER": "alma_app",
    "DB_PASSWORD": "Clave1*SeguraDePrueba",
    "DB_DRIVER": "ODBC Driver 18 for SQL Server",
    "DB_ENCRYPT": "1",
    "DB_TRUST_SERVER_CERTIFICATE": "0",
    "DB_POOL": "",
    "FLASK_DEBUG": "",
    "ZONA_HORARIA_BD": "UTC",
}


@pytest.fixture()
def produccion(monkeypatch):
    for variable, valor in VARIABLES_PRODUCCION.items():
        monkeypatch.setenv(variable, valor)
    return monkeypatch


def prueba_configuracion_de_produccion_segura(produccion):
    configuracion = cargar_configuracion()
    assert configuracion["DEBUG"] is False
    assert configuracion["SESSION_COOKIE_SECURE"] is True
    assert configuracion["SESSION_COOKIE_NAME"] == "__Host-alma_sesion"
    assert configuracion["HSTS"] is True
    assert configuracion["PROXY_SALTOS"] == 1
    assert configuracion["CARPETA_REGISTROS"] is None
    assert configuracion["SQLALCHEMY_ENGINE_OPTIONS"]["poolclass"] is NullPool
    assert "Encrypt%3Dyes" in configuracion["SQLALCHEMY_DATABASE_URI"]
    assert "TrustServerCertificate%3Dno" in configuracion["SQLALCHEMY_DATABASE_URI"]


@pytest.mark.parametrize(
    ("variable", "valor", "mensaje"),
    [
        ("SECRET_KEY", "", "SECRET_KEY"),
        ("SECRET_KEY", "demasiado-corta", "SECRET_KEY"),
        ("FLASK_DEBUG", "1", "FLASK_DEBUG"),
        ("DB_HOST", "", "DB_HOST"),
        ("DB_PASSWORD", "", "DB_USER"),
        ("DB_TRUST_SERVER_CERTIFICATE", "1", "DB_ENCRYPT"),
        ("DB_ENCRYPT", "0", "DB_ENCRYPT"),
    ],
)
def prueba_configuracion_insegura_impide_iniciar(produccion, variable, valor, mensaje):
    produccion.setenv(variable, valor)
    with pytest.raises(ConfiguracionInvalida, match=mensaje):
        cargar_configuracion()


def prueba_entorno_desconocido_se_rechaza(monkeypatch):
    monkeypatch.setenv("APP_ENV", "staging")
    with pytest.raises(ConfiguracionInvalida):
        cargar_configuracion()


def prueba_aplicacion_de_produccion_detras_de_proxy(produccion):
    from core.aplicacion import crear_app

    aplicacion = crear_app()

    @aplicacion.get("/eco-proxy")
    def eco_proxy():
        return {"ip": request.remote_addr, "esquema": request.scheme}

    cliente_http = aplicacion.test_client()
    cabeceras = {"X-Forwarded-For": "203.0.113.7", "X-Forwarded-Proto": "https"}
    assert cliente_http.get("/eco-proxy", headers=cabeceras).get_json() == {
        "ip": "203.0.113.7",
        "esquema": "https",
    }
    respuesta = cliente_http.get("/login", headers=cabeceras)
    assert respuesta.status_code == 200
    assert respuesta.headers["Strict-Transport-Security"].startswith("max-age=31536000")
    cookie = respuesta.headers["Set-Cookie"]
    assert cookie.startswith("__Host-alma_sesion=")
    assert "Secure" in cookie and "HttpOnly" in cookie and "SameSite=Lax" in cookie
    assert aplicacion.debug is False
    assert cliente_http.get("/salud").status_code == 200


def prueba_hora_de_la_base_se_muestra_en_hora_local(produccion):
    from core.aplicacion import _hora_local, crear_app

    with crear_app().app_context():
        assert _hora_local(datetime(2026, 11, 8, 18, 30, 0)) == "08/11/2026 12:30:00"
        assert _hora_local(None) == "—"


def prueba_servidor_de_desarrollo_bloqueado_en_produccion(produccion):
    import run

    with pytest.raises(SystemExit, match="gunicorn"):
        run.iniciar_desarrollo()
