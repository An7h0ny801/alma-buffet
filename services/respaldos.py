import logging
import re

import pyodbc
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from core.base_datos import db
from core.bitacoras import CLAVE_EMPLEADO, id_empleado_actual


TIPOS_RESPALDO = {
    "COMPLETO": "Completo",
    "DIFERENCIAL": "Diferencial",
    "LOG": "Registro de transacciones (log)",
}

TIPOS_MSDB = {"D": "COMPLETO", "I": "DIFERENCIAL", "L": "LOG"}

LIMITE_HISTORIAL = 100
MOTOR_AZURE_SQL = 5
PRIMER_ERROR_DE_USUARIO = 50000
MENSAJE_GENERICO = "No se pudo generar el respaldo. Revise el registro del servidor."

_MENSAJE_SQL = re.compile(r"\[SQL Server\](.*?)\s*\((\d+)\)\s*(?:\(SQL\w+\))?\s*$")

registro = logging.getLogger(__name__)


def _mensaje_sql_server(error):
    detalle = str(error.args[-1]) if error.args else str(error)
    coincidencia = _MENSAJE_SQL.search(detalle)
    if coincidencia and int(coincidencia.group(2)) >= PRIMER_ERROR_DE_USUARIO:
        return coincidencia.group(1).strip()
    return None


def _validar_texto(valor, maximo, campo):
    valor = (valor or "").strip()
    if len(valor) > maximo:
        raise ValueError(f"{campo} no puede superar {maximo} caracteres.")
    return valor or None


def generar_respaldo(tipo, *, descripcion="", verificar=True):
    tipo = (tipo or "").strip().upper()
    if tipo not in TIPOS_RESPALDO:
        raise ValueError("Seleccione un tipo de respaldo válido.")
    descripcion = _validar_texto(descripcion, 200, "La descripción")

    conexion = db.engine.connect().execution_options(isolation_level="AUTOCOMMIT")
    try:
        cursor = conexion.connection.cursor()
        cursor.execute(
            "EXEC sp_set_session_context @key = ?, @value = ?",
            CLAVE_EMPLEADO,
            id_empleado_actual(),
        )
        cursor.execute(
            "EXEC dbo.pa_RespaldarBase @pTipo = ?, @pDescripcion = ?, @pVerificar = ?",
            tipo,
            descripcion,
            1 if verificar else 0,
        )
        resultado = None
        while True:
            if cursor.description:
                columnas = [columna[0] for columna in cursor.description]
                fila = cursor.fetchone()
                if fila:
                    resultado = dict(zip(columnas, fila))
            if not cursor.nextset():
                break
        cursor.close()
    except pyodbc.Error as error:
        mensaje = _mensaje_sql_server(error)
        if not mensaje:
            registro.error("Error al generar un respaldo", exc_info=error)
        raise ValueError(mensaje or MENSAJE_GENERICO) from error
    finally:
        conexion.close()

    if not resultado:
        raise ValueError("SQL Server no devolvió el resultado del respaldo.")
    return resultado


def _historial_servidor():
    try:
        filas = db.session.execute(
            text(
                "SELECT TOP (:limite) bs.backup_start_date AS inicio, "
                "bs.backup_finish_date AS fin, bs.type AS tipo, "
                "bs.compressed_backup_size AS tamano, bs.user_name AS usuario, "
                "mf.physical_device_name AS archivo, bs.name AS nombre "
                "FROM msdb.dbo.backupset AS bs "
                "JOIN msdb.dbo.backupmediafamily AS mf ON mf.media_set_id = bs.media_set_id "
                "WHERE bs.database_name = DB_NAME() "
                "ORDER BY bs.backup_finish_date DESC"
            ),
            {"limite": LIMITE_HISTORIAL},
        ).mappings().all()
    except DBAPIError:
        db.session.rollback()
        return None
    return [
        dict(fila, tipo=TIPOS_MSDB.get(fila["tipo"], fila["tipo"])) for fila in filas
    ]


def datos_respaldos():
    base = db.session.execute(
        text(
            "SELECT DB_NAME() AS nombre, d.recovery_model_desc AS modelo, "
            "CAST(SERVERPROPERTY('InstanceDefaultBackupPath') AS NVARCHAR(260)) AS carpeta, "
            "CAST(SERVERPROPERTY('Edition') AS NVARCHAR(128)) AS edicion, "
            "CAST(SERVERPROPERTY('EngineEdition') AS INT) AS motor, "
            "(SELECT CAST(SUM(CAST(size AS BIGINT)) * 8 / 1024.0 AS DECIMAL(12, 2)) "
            " FROM sys.database_files) AS tamanoMB "
            "FROM sys.databases AS d WHERE d.name = DB_NAME()"
        )
    ).mappings().one()
    azure = base["motor"] == MOTOR_AZURE_SQL
    historial = db.session.execute(
        text(
            "SELECT TOP (:limite) * FROM dbo.vHistorialRespaldos "
            "ORDER BY fechaInicio DESC, idRespaldo DESC"
        ),
        {"limite": LIMITE_HISTORIAL},
    ).mappings().all()
    servidor = None if azure else _historial_servidor()

    ultimos = {}
    for fila in servidor if servidor is not None else historial:
        tipo = fila["tipo"]
        if fila.get("estado", "EXITOSO") == "EXITOSO" and tipo not in ultimos:
            ultimos[tipo] = fila.get("fin") or fila.get("fechaFin")

    return {
        "base": base,
        "historial": historial,
        "servidor": servidor,
        "ultimos": ultimos,
        "tipos": TIPOS_RESPALDO,
        "admite_log": base["modelo"] != "SIMPLE",
        "azure": azure,
    }
