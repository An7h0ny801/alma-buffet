import shutil

import pytest

from core import migraciones
from core.configuracion import ConfiguracionInvalida
from core.usuario_bd import sentencias_permisos, validar_password_bd, validar_usuario


BASE_ADOPCION = "BUFFET_ALMA_PRUEBAS_ADOPCION"


def _consulta(nombre, sql):
    with migraciones.conectar(nombre) as conexion:
        return conexion.cursor().execute(sql).fetchall()


@pytest.fixture()
def base_temporal():
    migraciones.eliminar_base(BASE_ADOPCION)
    migraciones.crear_base_si_falta(BASE_ADOPCION)
    yield BASE_ADOPCION
    migraciones.eliminar_base(BASE_ADOPCION)


def prueba_base_existente_sin_control_se_adopta(base_temporal):
    inicial = migraciones.migraciones_disponibles()[0]
    with migraciones.conectar(base_temporal) as conexion:
        migraciones.ejecutar_lotes(conexion.cursor(), inicial.lotes)
    resultado = migraciones.aplicar_migraciones(base_temporal)
    assert resultado["adoptadas"] == ["0001_esquema_inicial.sql"]
    assert resultado["aplicadas"] == ["0002_seguridad_produccion.sql"]
    modos = dict(_consulta(base_temporal, "SELECT nombre, modo FROM TblMigraciones"))
    assert modos == {
        "0001_esquema_inicial.sql": "EXISTENTE",
        "0002_seguridad_produccion.sql": "APLICADA",
    }
    parametros = {
        fila[0]
        for fila in _consulta(
            base_temporal,
            "SELECT name FROM sys.parameters WHERE object_id = OBJECT_ID(N'dbo.pa_RespaldarBase')",
        )
    }
    assert parametros == {"@pTipo", "@pDescripcion", "@pVerificar"}


def prueba_base_con_otro_esquema_se_rechaza(base_temporal):
    with migraciones.conectar(base_temporal) as conexion:
        conexion.cursor().execute("CREATE TABLE dbo.TblAjena (idAjena INT NOT NULL)")
    with pytest.raises(migraciones.ErrorMigracion, match="no coincide"):
        migraciones.aplicar_migraciones(base_temporal)


def prueba_migracion_modificada_se_detecta(base_temporal, tmp_path):
    carpeta = tmp_path / "migrations"
    shutil.copytree(migraciones.CARPETA_MIGRACIONES, carpeta)
    migraciones.aplicar_migraciones(base_temporal, carpeta)
    ruta = carpeta / "0002_seguridad_produccion.sql"
    ruta.write_text(ruta.read_text(encoding="utf-8") + "\nSELECT 1\nGO\n", encoding="utf-8")
    with pytest.raises(migraciones.ErrorMigracion, match="cambió después de aplicarse"):
        migraciones.aplicar_migraciones(base_temporal, carpeta)


def prueba_migracion_fallida_no_deja_cambios(base_temporal, tmp_path):
    carpeta = tmp_path / "migrations"
    shutil.copytree(migraciones.CARPETA_MIGRACIONES, carpeta)
    (carpeta / "0003_rota.sql").write_text(
        "CREATE TABLE dbo.TblTemporal (idTemporal INT NOT NULL)\nGO\nSELECT * FROM dbo.TablaQueNoExiste\nGO\n",
        encoding="utf-8",
    )
    with pytest.raises(migraciones.ErrorMigracion, match="0003_rota.sql"):
        migraciones.aplicar_migraciones(base_temporal, carpeta)
    aplicadas = {fila[0] for fila in _consulta(base_temporal, "SELECT nombre FROM TblMigraciones")}
    assert "0003_rota.sql" not in aplicadas
    assert not _consulta(base_temporal, "SELECT 1 FROM sys.tables WHERE name = 'TblTemporal'")


def prueba_nombres_invalidos_se_rechazan(tmp_path):
    (tmp_path / "sin_numero.sql").write_text("SELECT 1", encoding="utf-8")
    with pytest.raises(migraciones.ErrorMigracion):
        migraciones.migraciones_disponibles(tmp_path)
    with pytest.raises(migraciones.ErrorMigracion):
        migraciones.validar_nombre_base("base]; DROP DATABASE x; --")


def prueba_en_produccion_no_se_crean_ni_eliminan_bases(monkeypatch):
    monkeypatch.setenv("APP_ENV", "produccion")
    with pytest.raises(ConfiguracionInvalida):
        migraciones.crear_base_si_falta("CUALQUIERA")
    with pytest.raises(ConfiguracionInvalida):
        migraciones.eliminar_base("CUALQUIERA")


def prueba_usuario_de_base_con_permisos_minimos():
    sentencias = sentencias_permisos("alma_app", azure=True)
    assert "ALTER ROLE [db_datareader] ADD MEMBER [alma_app];" in sentencias
    assert "GRANT EXECUTE ON SCHEMA::[dbo] TO [alma_app];" in sentencias
    assert "DENY INSERT, UPDATE, DELETE ON [dbo].[TblAuditoriaSeguridad] TO [alma_app];" in sentencias
    assert not any("db_owner" in s or "db_ddladmin" in s or "CREATE ANY DATABASE" in s for s in sentencias)
    assert not any("db_backupoperator" in s for s in sentencias)
    assert any("db_backupoperator" in s for s in sentencias_permisos("alma_app", azure=False))
    with pytest.raises(ValueError):
        validar_usuario("alma];DROP")
    with pytest.raises(ValueError):
        validar_password_bd("Corta1*")
