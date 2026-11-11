import hashlib
import logging
import re
from dataclasses import dataclass
from pathlib import Path

from core.base_datos import conectar_sql_server
from core.configuracion import (
    RAIZ_PROYECTO,
    ConfiguracionInvalida,
    cadena_odbc,
    credenciales_migracion,
    es_produccion,
    nombre_base,
)


CARPETA_MIGRACIONES = RAIZ_PROYECTO / "migrations"
INTERCALACION = "Modern_Spanish_CI_AS"
RECURSO_BLOQUEO = "AlmaBuffet.Migraciones"
ESPERA_BLOQUEO_MS = 120000

_SEPARADOR_LOTES = re.compile(r"^\s*GO\s*$", re.MULTILINE | re.IGNORECASE)
_NOMBRE_MIGRACION = re.compile(r"^\d{4}_[a-z0-9_]+\.sql$")
_NOMBRE_BASE = re.compile(r"^[A-Za-z0-9_]{1,128}$")
_OBJETO_CREADO = re.compile(
    r"^CREATE\s+(?:OR\s+ALTER\s+)?(?:TABLE|PROCEDURE|FUNCTION|VIEW|TRIGGER)\s+"
    r"(?:\[dbo\]\.|dbo\.)?\[?(\w+)\]?",
    re.MULTILINE | re.IGNORECASE,
)

_CREAR_TABLA_MIGRACIONES = """
IF OBJECT_ID(N'dbo.TblMigraciones', N'U') IS NULL
CREATE TABLE [dbo].[TblMigraciones] (
    [idMigracion]      INT IDENTITY(1, 1) NOT NULL,
    [nombre]           NVARCHAR(200) NOT NULL,
    [sumaVerificacion] CHAR(64)      NOT NULL,
    [modo]             VARCHAR(10)   NOT NULL CONSTRAINT [DF_TblMigraciones_modo] DEFAULT ('APLICADA'),
    [fechaAplicacion]  DATETIME2(3)  NOT NULL CONSTRAINT [DF_TblMigraciones_fechaAplicacion] DEFAULT (SYSDATETIME()),
    CONSTRAINT [PK_TblMigraciones] PRIMARY KEY CLUSTERED ([idMigracion]),
    CONSTRAINT [UQ_TblMigraciones_nombre] UNIQUE ([nombre]),
    CONSTRAINT [CK_TblMigraciones_modo] CHECK ([modo] IN ('APLICADA', 'EXISTENTE'))
);
"""

registro = logging.getLogger(__name__)


class ErrorMigracion(RuntimeError):
    pass


@dataclass(frozen=True)
class Migracion:
    nombre: str
    contenido: str

    @property
    def suma(self):
        return hashlib.sha256(self.contenido.encode("utf-8")).hexdigest()

    @property
    def lotes(self):
        return dividir_lotes(self.contenido)

    @property
    def objetos(self):
        return {nombre for nombre in _OBJETO_CREADO.findall(self.contenido)}


def dividir_lotes(contenido):
    return [lote.strip() for lote in _SEPARADOR_LOTES.split(contenido) if lote.strip()]


def leer_sql(ruta):
    return Path(ruta).read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def migraciones_disponibles(carpeta=CARPETA_MIGRACIONES):
    migraciones = []
    for ruta in sorted(Path(carpeta).glob("*.sql")):
        if not _NOMBRE_MIGRACION.fullmatch(ruta.name):
            raise ErrorMigracion(f"Nombre de migración inválido: {ruta.name}")
        migraciones.append(Migracion(ruta.name, leer_sql(ruta)))
    return migraciones


def validar_nombre_base(nombre):
    if not _NOMBRE_BASE.fullmatch(nombre or ""):
        raise ErrorMigracion("El nombre de la base solo puede tener letras, números y guiones bajos.")
    return nombre


def conectar(nombre=None, autocommit=True):
    return conectar_sql_server(
        cadena_odbc(nombre, credenciales=credenciales_migracion()), autocommit=autocommit
    )


def ejecutar_lotes(cursor, lotes):
    for lote in lotes:
        cursor.execute(lote)
        while cursor.nextset():
            pass


def crear_base_si_falta(nombre=None):
    if es_produccion():
        raise ConfiguracionInvalida(
            "En producción la base de datos se crea desde el proveedor (por ejemplo, el portal de Azure)."
        )
    nombre = validar_nombre_base(nombre or nombre_base())
    with conectar("master") as conexion:
        cursor = conexion.cursor()
        if cursor.execute("SELECT DB_ID(?)", nombre).fetchval() is not None:
            return False
        cursor.execute(f"CREATE DATABASE [{nombre}] COLLATE {INTERCALACION}")
    return True


def eliminar_base(nombre):
    if es_produccion():
        raise ConfiguracionInvalida("No se permite eliminar bases de datos en producción.")
    nombre = validar_nombre_base(nombre)
    with conectar("master") as conexion:
        conexion.cursor().execute(
            f"IF DB_ID(N'{nombre}') IS NOT NULL BEGIN "
            f"ALTER DATABASE [{nombre}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; "
            f"DROP DATABASE [{nombre}]; END"
        )


def _aplicadas(cursor):
    return {
        fila.nombre: fila.sumaVerificacion
        for fila in cursor.execute("SELECT nombre, sumaVerificacion FROM dbo.TblMigraciones")
    }


def _objetos_existentes(cursor):
    return {
        fila[0]
        for fila in cursor.execute(
            "SELECT name FROM sys.objects UNION SELECT name FROM sys.triggers"
        )
    }


def _hay_tablas_de_usuario(cursor):
    return bool(
        cursor.execute(
            "SELECT COUNT(*) FROM sys.tables WHERE name <> N'TblMigraciones'"
        ).fetchval()
    )


def _registrar(cursor, migracion, modo):
    cursor.execute(
        "INSERT INTO dbo.TblMigraciones (nombre, sumaVerificacion, modo) VALUES (?, ?, ?)",
        migracion.nombre,
        migracion.suma,
        modo,
    )


def _bloquear(cursor):
    resultado = cursor.execute(
        "DECLARE @vResultado INT; "
        "EXEC @vResultado = sp_getapplock @Resource = ?, @LockMode = 'Exclusive', "
        "@LockOwner = 'Session', @LockTimeout = ?; SELECT @vResultado;",
        RECURSO_BLOQUEO,
        ESPERA_BLOQUEO_MS,
    ).fetchval()
    if resultado is None or resultado < 0:
        raise ErrorMigracion("Otra instancia está aplicando migraciones; inténtelo más tarde.")


def _adoptar_base_existente(cursor, migraciones, aplicadas):
    if aplicadas or not migraciones or not _hay_tablas_de_usuario(cursor):
        return []
    inicial = migraciones[0]
    faltantes = inicial.objetos - _objetos_existentes(cursor)
    if faltantes:
        raise ErrorMigracion(
            "La base ya contiene tablas, pero no coincide con el esquema esperado. "
            f"Faltan: {', '.join(sorted(faltantes)[:10])}. Use una base vacía."
        )
    _registrar(cursor, inicial, "EXISTENTE")
    return [inicial.nombre]


def aplicar_migraciones(nombre=None, carpeta=CARPETA_MIGRACIONES):
    nombre = validar_nombre_base(nombre or nombre_base())
    migraciones = migraciones_disponibles(carpeta)
    resultado = {"adoptadas": [], "aplicadas": []}
    with conectar(nombre, autocommit=True) as conexion:
        cursor = conexion.cursor()
        _bloquear(cursor)
        cursor.execute(_CREAR_TABLA_MIGRACIONES)
        aplicadas = _aplicadas(cursor)
        resultado["adoptadas"] = _adoptar_base_existente(cursor, migraciones, aplicadas)
        aplicadas = _aplicadas(cursor)
        for migracion in migraciones:
            if migracion.nombre in aplicadas:
                if aplicadas[migracion.nombre] != migracion.suma:
                    raise ErrorMigracion(
                        f"La migración {migracion.nombre} cambió después de aplicarse. "
                        "Cree una migración nueva en lugar de editar una existente."
                    )
                continue
            registro.info("Aplicando migración %s", migracion.nombre)
            conexion.autocommit = False
            try:
                ejecutar_lotes(cursor, migracion.lotes)
                _registrar(cursor, migracion, "APLICADA")
                conexion.commit()
            except Exception as error:
                conexion.rollback()
                raise ErrorMigracion(f"Falló la migración {migracion.nombre}: {error}") from error
            finally:
                conexion.autocommit = True
            resultado["aplicadas"].append(migracion.nombre)
    return resultado


def intercalacion_base(nombre=None):
    nombre = validar_nombre_base(nombre or nombre_base())
    with conectar(nombre) as conexion:
        return conexion.cursor().execute(
            "SELECT CAST(DATABASEPROPERTYEX(DB_NAME(), 'Collation') AS NVARCHAR(128))"
        ).fetchval()


def cargar_script(ruta, nombre=None):
    nombre = validar_nombre_base(nombre or nombre_base())
    with conectar(nombre, autocommit=True) as conexion:
        ejecutar_lotes(conexion.cursor(), dividir_lotes(leer_sql(ruta)))
