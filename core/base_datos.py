import logging
import time

import pyodbc
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine


db = SQLAlchemy(session_options={"expire_on_commit": False})

BLOQUEO_FILA = "WITH (UPDLOCK, ROWLOCK)"

ERRORES_TRANSITORIOS = ("40613", "40197", "40501", "49918", "49919", "49920", "4221")
REINTENTOS_CONEXION = 5
ESPERA_INICIAL_SEGUNDOS = 5

registro = logging.getLogger(__name__)


def es_error_transitorio(error):
    texto = " ".join(str(argumento) for argumento in getattr(error, "args", ()))
    return any(codigo in texto for codigo in ERRORES_TRANSITORIOS)


def _con_reintentos(conectar):
    espera = ESPERA_INICIAL_SEGUNDOS
    for intento in range(1, REINTENTOS_CONEXION + 1):
        try:
            return conectar()
        except pyodbc.Error as error:
            if intento == REINTENTOS_CONEXION or not es_error_transitorio(error):
                raise
            registro.warning(
                "La base de datos no está disponible (intento %s de %s); se reintentará en %s s.",
                intento,
                REINTENTOS_CONEXION,
                espera,
            )
            time.sleep(espera)
            espera = min(espera * 2, 20)


def conectar_sql_server(cadena, autocommit=True):
    return _con_reintentos(lambda: pyodbc.connect(cadena, autocommit=autocommit))


@event.listens_for(Engine, "do_connect")
def _conectar_motor(dialecto, registro_conexion, argumentos, parametros):
    if dialecto.name != "mssql":
        return None
    return _con_reintentos(lambda: dialecto.connect(*argumentos, **parametros))
