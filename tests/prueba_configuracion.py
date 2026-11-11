import sys
import types

from core import configuracion


def _winreg_falso(instancias):
    modulo = types.ModuleType("winreg")
    modulo.HKEY_LOCAL_MACHINE = 0
    modulo.KEY_READ = 0
    modulo.KEY_WOW64_64KEY = 0

    class Clave:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def abrir(*args):
        if instancias is None:
            raise OSError("SQL Server no instalado")
        return Clave()

    modulo.OpenKey = abrir
    modulo.QueryInfoKey = lambda clave: (0, len(instancias), 0)
    modulo.EnumValue = lambda clave, indice: (instancias[indice], "", 1)
    return modulo


def prueba_instancia_predeterminada(monkeypatch):
    monkeypatch.setitem(sys.modules, "winreg", _winreg_falso(["MSSQLSERVER"]))
    assert configuracion._instancia_local() == "localhost"


def prueba_instancia_express(monkeypatch):
    monkeypatch.setitem(sys.modules, "winreg", _winreg_falso(["SQLEXPRESS"]))
    assert configuracion._instancia_local() == r"localhost\SQLEXPRESS"


def prueba_sin_sql_server_instalado(monkeypatch):
    monkeypatch.setitem(sys.modules, "winreg", _winreg_falso(None))
    assert configuracion._instancia_local() == "localhost"


def prueba_db_host_tiene_prioridad(monkeypatch):
    monkeypatch.setenv("DB_HOST", r"SERVIDOR\INSTANCIA")
    assert configuracion.servidor_sql() == r"SERVIDOR\INSTANCIA"


def prueba_las_migraciones_son_portables_y_sin_credenciales():
    from core.migraciones import migraciones_disponibles

    migraciones = migraciones_disponibles()
    assert [m.nombre for m in migraciones][:2] == [
        "0001_esquema_inicial.sql",
        "0002_seguridad_produccion.sql",
    ]
    for migracion in migraciones:
        contenido = migracion.contenido
        assert "USE [" not in contenido
        assert "ALTER DATABASE" not in contenido
        assert "BUFFET_ALMA_PRUEBA_33" not in contenido
        assert "MSSQL17" not in contenido
        assert "INSERT [dbo].[TblUsuarios]" not in contenido
        assert "INSERT [dbo].[TblEmpleados]" not in contenido
        assert "scrypt:" not in contenido and "$argon2" not in contenido


def prueba_cadena_odbc_cifrada_y_con_valores_escapados(monkeypatch):
    monkeypatch.setenv("DB_HOST", "servidor.database.windows.net")
    monkeypatch.setenv("DB_PORT", "1433")
    monkeypatch.setenv("DB_USER", "alma_app")
    monkeypatch.setenv("DB_PASSWORD", "a}b;c=d")
    monkeypatch.setenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
    monkeypatch.setenv("DB_TRUST_SERVER_CERTIFICATE", "0")
    cadena = configuracion.cadena_odbc("BASE")
    assert "SERVER={servidor.database.windows.net,1433}" in cadena
    assert "Encrypt=yes" in cadena
    assert "TrustServerCertificate=no" in cadena
    assert "PWD={a}}b;c=d}" in cadena
    assert "Trusted_Connection" not in cadena


def prueba_credenciales_de_migracion_separadas(monkeypatch):
    monkeypatch.setenv("DB_USER", "alma_app")
    monkeypatch.setenv("DB_PASSWORD", "clave_app")
    monkeypatch.setenv("DB_MIGRACION_USER", "")
    assert configuracion.credenciales_migracion() == ("alma_app", "clave_app")
    monkeypatch.setenv("DB_MIGRACION_USER", "duenio")
    monkeypatch.setenv("DB_MIGRACION_PASSWORD", "clave_duenio")
    assert configuracion.credenciales_migracion() == ("duenio", "clave_duenio")
