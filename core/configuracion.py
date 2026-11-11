import os
import secrets
from datetime import timedelta
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy.pool import NullPool


RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
NOMBRE_BASE_PREDETERMINADO = "BUFFET_ALMA_PRUEBA_33"
ENTORNOS = ("desarrollo", "produccion", "pruebas")
LONGITUD_MINIMA_SECRETO = 32

load_dotenv(RAIZ_PROYECTO / ".env")


class ConfiguracionInvalida(RuntimeError):
    pass


def entorno():
    valor = os.getenv("APP_ENV", "desarrollo").strip().lower()
    if valor not in ENTORNOS:
        raise ConfiguracionInvalida(
            f"APP_ENV debe ser uno de: {', '.join(ENTORNOS)}."
        )
    return valor


def es_produccion():
    return entorno() == "produccion"


def variable_booleana(nombre, predeterminado=False):
    valor = os.getenv(nombre)
    if valor is None or not valor.strip():
        return predeterminado
    return valor.strip().lower() in {"1", "true", "yes", "on", "si", "sí"}


def variable_entera(nombre, predeterminado):
    valor = os.getenv(nombre)
    if valor is None or not valor.strip():
        return predeterminado
    try:
        return int(valor)
    except ValueError as error:
        raise ConfiguracionInvalida(f"{nombre} debe ser un número entero.") from error


def _instancia_local():
    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Microsoft SQL Server\Instance Names\SQL",
            0,
            winreg.KEY_READ | winreg.KEY_WOW64_64KEY,
        ) as clave:
            instancias = [
                winreg.EnumValue(clave, indice)[0]
                for indice in range(winreg.QueryInfoKey(clave)[1])
            ]
    except (ImportError, OSError):
        return "localhost"
    if not instancias or "MSSQLSERVER" in instancias:
        return "localhost"
    return "localhost\\" + instancias[0]


def servidor_sql():
    servidor = os.getenv("DB_HOST", "").strip()
    if servidor:
        return servidor
    if es_produccion():
        raise ConfiguracionInvalida("DB_HOST es obligatorio en producción.")
    return _instancia_local()


def nombre_base():
    return os.getenv("DB_NAME", "").strip() or NOMBRE_BASE_PREDETERMINADO


def _controlador_odbc():
    controlador = os.getenv("DB_DRIVER", "").strip()
    if controlador:
        return controlador
    try:
        import pyodbc

        instalados = [
            nombre
            for nombre in pyodbc.drivers()
            if nombre.startswith("ODBC Driver") and nombre.endswith("for SQL Server")
        ]
    except Exception:
        instalados = []
    if instalados:
        return sorted(instalados, key=lambda nombre: int(nombre.split()[2]))[-1]
    return "ODBC Driver 18 for SQL Server"


def _valor_odbc(valor):
    return "{" + str(valor).replace("}", "}}") + "}"


def credenciales_aplicacion():
    return os.getenv("DB_USER", "").strip(), os.getenv("DB_PASSWORD", "")


def credenciales_migracion():
    usuario = os.getenv("DB_MIGRACION_USER", "").strip()
    if usuario:
        return usuario, os.getenv("DB_MIGRACION_PASSWORD", "")
    return credenciales_aplicacion()


def cifrado_conexion():
    cifrar = variable_booleana("DB_ENCRYPT", True)
    confiar = variable_booleana("DB_TRUST_SERVER_CERTIFICATE", not es_produccion())
    return cifrar, confiar


def cadena_odbc(nombre=None, credenciales=None):
    servidor = servidor_sql()
    puerto = os.getenv("DB_PORT", "").strip()
    if puerto:
        servidor = f"{servidor},{puerto}"
    usuario, password = credenciales or credenciales_aplicacion()
    cifrar, confiar = cifrado_conexion()
    partes = [
        f"DRIVER={_valor_odbc(_controlador_odbc())}",
        f"SERVER={_valor_odbc(servidor)}",
        f"DATABASE={_valor_odbc(nombre or nombre_base())}",
        f"Encrypt={'yes' if cifrar else 'no'}",
        f"TrustServerCertificate={'yes' if confiar else 'no'}",
        f"Connection Timeout={variable_entera('DB_TIMEOUT', 30)}",
        "APP=AlmaBuffet",
    ]
    if usuario:
        partes += [f"UID={_valor_odbc(usuario)}", f"PWD={_valor_odbc(password)}"]
    else:
        partes.append("Trusted_Connection=yes")
    return ";".join(partes) + ";"


def url_base_datos(nombre=None):
    return "mssql+pyodbc:///?odbc_connect=" + quote_plus(cadena_odbc(nombre))


def _opciones_motor():
    tipo = os.getenv("DB_POOL", "").strip().lower() or ("nulo" if es_produccion() else "cola")
    if tipo == "nulo":
        return {"poolclass": NullPool}
    return {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "pool_size": variable_entera("DB_POOL_SIZE", 5),
        "max_overflow": variable_entera("DB_POOL_MAX_OVERFLOW", 5),
    }


def _validar_produccion(configuracion):
    errores = []
    if len(configuracion["SECRET_KEY"] or "") < LONGITUD_MINIMA_SECRETO:
        errores.append(
            f"SECRET_KEY es obligatoria y debe tener al menos {LONGITUD_MINIMA_SECRETO} caracteres."
        )
    if variable_booleana("FLASK_DEBUG"):
        errores.append("FLASK_DEBUG no puede estar activo en producción.")
    if not os.getenv("DB_HOST", "").strip():
        errores.append("DB_HOST es obligatorio.")
    usuario, password = credenciales_aplicacion()
    if not usuario or not password:
        errores.append("DB_USER y DB_PASSWORD son obligatorios.")
    cifrar, confiar = cifrado_conexion()
    if not cifrar or confiar:
        errores.append("La conexión debe usar DB_ENCRYPT=1 y DB_TRUST_SERVER_CERTIFICATE=0.")
    if errores:
        raise ConfiguracionInvalida("Configuración de producción inválida. " + " ".join(errores))


def cargar_configuracion():
    actual = entorno()
    produccion = actual == "produccion"
    secreto = os.getenv("SECRET_KEY", "").strip()
    configuracion = {
        "ENTORNO": actual,
        "DEBUG": False if produccion else variable_booleana("FLASK_DEBUG"),
        "TESTING": actual == "pruebas",
        "SECRET_KEY": secreto or (None if produccion else secrets.token_hex(32)),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SQLALCHEMY_ENGINE_OPTIONS": _opciones_motor(),
        "SESSION_COOKIE_NAME": "__Host-alma_sesion" if produccion else "alma_sesion",
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": produccion or variable_booleana("SESSION_COOKIE_SECURE"),
        "PERMANENT_SESSION_LIFETIME": timedelta(hours=variable_entera("SESION_DURACION_HORAS", 8)),
        "SESION_INACTIVIDAD_MINUTOS": variable_entera("SESION_INACTIVIDAD_MINUTOS", 60),
        "MAX_CONTENT_LENGTH": 1024 * 1024,
        "SEND_FILE_MAX_AGE_DEFAULT": 3600 if produccion else 0,
        "HSTS": produccion,
        "PROXY_SALTOS": variable_entera("PROXY_SALTOS", 1 if produccion else 0),
        "LOGIN_MAX_INTENTOS": variable_entera("LOGIN_MAX_INTENTOS", 5),
        "LOGIN_MAX_INTENTOS_IP": variable_entera("LOGIN_MAX_INTENTOS_IP", 20),
        "LOGIN_VENTANA_MINUTOS": variable_entera("LOGIN_VENTANA_MINUTOS", 15),
        "ZONA_HORARIA": os.getenv("ZONA_HORARIA", "").strip() or "America/Costa_Rica",
        "ZONA_HORARIA_BD": os.getenv("ZONA_HORARIA_BD", "").strip(),
        "CARPETA_REGISTROS": None if produccion else (
            os.getenv("LOG_DIR", "").strip() or str(RAIZ_PROYECTO / "logs")
        ),
    }
    if produccion:
        _validar_produccion(configuracion)
    configuracion["SQLALCHEMY_DATABASE_URI"] = url_base_datos()
    return configuracion
