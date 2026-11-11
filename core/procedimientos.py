import re

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from core.base_datos import db


_MENSAJE_SQL_SERVER = re.compile(r"\[SQL Server\](.+?)\s*\((\d+)\)\s*\(SQL")
PRIMER_ERROR_DE_USUARIO = 50000


def mensaje_base_datos(error):
    coincidencia = _MENSAJE_SQL_SERVER.search(str(getattr(error, "orig", error)))
    if not coincidencia or int(coincidencia.group(2)) < PRIMER_ERROR_DE_USUARIO:
        return None
    return coincidencia.group(1).strip()


def ejecutar_procedimiento(nombre, **parametros):
    argumentos = ", ".join(f"@{clave} = :{clave}" for clave in parametros)
    sentencia = text(f"EXEC dbo.{nombre} {argumentos}".strip())
    try:
        resultado = db.session.execute(sentencia, parametros)
        return resultado.mappings().all() if resultado.returns_rows else []
    except DBAPIError as error:
        mensaje = mensaje_base_datos(error)
        if mensaje:
            raise ValueError(mensaje) from error
        raise


def total_ticket(id_ticket):
    return db.session.execute(
        text("SELECT dbo.fn_TotalTicket(:id_ticket)"),
        {"id_ticket": id_ticket},
    ).scalar()
