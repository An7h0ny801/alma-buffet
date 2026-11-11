import re

from core import migraciones
from core.configuracion import nombre_base
from services.validaciones import validar_password


TABLAS_PROTEGIDAS = (
    "TblHistorialProductos",
    "TblHistorialReservaciones",
    "TblHistorialDetalleTicket",
    "TblAuditoriaCaja",
    "TblAuditoriaSeguridad",
    "TblAuditoriaSesiones",
    "TblHistorialRespaldos",
    "TblMigraciones",
)
LONGITUD_MINIMA = 12
MOTOR_AZURE_SQL = 5

_NOMBRE_USUARIO = re.compile(r"^[A-Za-z][A-Za-z0-9_]{2,63}$")

_USUARIO_CONTENIDO = (
    "DECLARE @vSql NVARCHAR(MAX) = CASE WHEN DATABASE_PRINCIPAL_ID(?) IS NULL "
    "THEN N'CREATE USER ' ELSE N'ALTER USER ' END "
    "+ QUOTENAME(?) + N' WITH PASSWORD = ' + QUOTENAME(?, '''') + N';'; EXEC (@vSql);"
)
_INICIO_SESION = (
    "DECLARE @vSql NVARCHAR(MAX) = CASE WHEN SUSER_ID(?) IS NULL "
    "THEN N'CREATE LOGIN ' ELSE N'ALTER LOGIN ' END "
    "+ QUOTENAME(?) + N' WITH PASSWORD = ' + QUOTENAME(?, '''') + N', CHECK_POLICY = ON;'; EXEC (@vSql);"
)
_USUARIO_DE_INICIO = (
    "DECLARE @vSql NVARCHAR(MAX) = N'CREATE USER ' + QUOTENAME(?) + N' FOR LOGIN ' + QUOTENAME(?) + N';'; "
    "IF DATABASE_PRINCIPAL_ID(?) IS NULL EXEC (@vSql);"
)


def validar_usuario(usuario):
    if not _NOMBRE_USUARIO.fullmatch(usuario or ""):
        raise ValueError(
            "El usuario debe empezar con una letra y tener solo letras, números o guiones bajos."
        )
    return usuario


def validar_password_bd(password):
    if len(password or "") < LONGITUD_MINIMA:
        raise ValueError(f"La contraseña debe tener al menos {LONGITUD_MINIMA} caracteres.")
    return validar_password(password)


def sentencias_permisos(usuario, azure):
    usuario = f"[{validar_usuario(usuario)}]"
    sentencias = [
        f"ALTER ROLE [db_datareader] ADD MEMBER {usuario};",
        f"ALTER ROLE [db_datawriter] ADD MEMBER {usuario};",
        f"GRANT EXECUTE ON SCHEMA::[dbo] TO {usuario};",
    ]
    sentencias += [
        f"DENY INSERT, UPDATE, DELETE ON [dbo].[{tabla}] TO {usuario};"
        for tabla in TABLAS_PROTEGIDAS
    ]
    if not azure:
        sentencias.append(f"ALTER ROLE [db_backupoperator] ADD MEMBER {usuario};")
    return sentencias


def crear_usuario_aplicacion(usuario, password):
    usuario = validar_usuario(usuario)
    validar_password_bd(password)
    nombre = migraciones.validar_nombre_base(nombre_base())
    with migraciones.conectar(nombre) as conexion:
        cursor = conexion.cursor()
        motor = cursor.execute("SELECT CAST(SERVERPROPERTY('EngineEdition') AS INT)").fetchval()
        azure = motor == MOTOR_AZURE_SQL
        if azure:
            cursor.execute(_USUARIO_CONTENIDO, usuario, usuario, password)
        else:
            with migraciones.conectar("master") as maestra:
                maestra.cursor().execute(_INICIO_SESION, usuario, usuario, password)
            cursor.execute(_USUARIO_DE_INICIO, usuario, usuario, usuario)
        for sentencia in sentencias_permisos(usuario, azure):
            cursor.execute(sentencia)
    if not azure:
        with migraciones.conectar("msdb") as msdb:
            cursor_msdb = msdb.cursor()
            cursor_msdb.execute(_USUARIO_DE_INICIO, usuario, usuario, usuario)
            cursor_msdb.execute(f"GRANT SELECT ON [dbo].[backupset] TO [{usuario}];")
            cursor_msdb.execute(f"GRANT SELECT ON [dbo].[backupmediafamily] TO [{usuario}];")
    return "Azure SQL Database" if azure else "SQL Server"
