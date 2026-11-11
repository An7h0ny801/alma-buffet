import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from core.base_datos import db
from tests.utilidades import consulta, crear_usuario, enviar, iniciar_sesion, texto, valor


def _ultimo_respaldo(app):
    return consulta(
        app,
        "SELECT TOP 1 tipo, estado, verificado, idEmpleado, archivo "
        "FROM TblHistorialRespaldos ORDER BY idRespaldo DESC",
    )[0]


def prueba_respaldo_completo_y_log(admin):
    app = admin.application
    respuesta = enviar(admin, "/respaldos/generar", {"tipo": "COMPLETO", "verificar": "1"})
    assert "Respaldo generado y verificado correctamente." in texto(respuesta)
    tipo, estado, verificado, id_empleado, archivo = _ultimo_respaldo(app)
    id_admin = valor(app, "SELECT idEmpleado FROM TblUsuarios WHERE correo = 'admin@alma.com'")
    assert (tipo, estado, verificado, id_empleado) == ("COMPLETO", "EXITOSO", True, id_admin)
    assert archivo.endswith(".bak")

    respuesta = enviar(admin, "/respaldos/generar", {"tipo": "DIFERENCIAL"})
    assert "Respaldo generado (sin verificar)." in texto(respuesta)
    assert _ultimo_respaldo(app)[:3] == ("DIFERENCIAL", "EXITOSO", False)

    modelo = valor(app, "SELECT recovery_model_desc FROM sys.databases WHERE name = DB_NAME()")
    if modelo != "SIMPLE":
        enviar(admin, "/respaldos/generar", {"tipo": "LOG", "verificar": "1"})
        assert _ultimo_respaldo(app)[:3] == ("LOG", "EXITOSO", True)

    pagina = texto(admin.get("/respaldos"))
    assert archivo in pagina


def prueba_la_carpeta_del_cliente_se_ignora(admin):
    app = admin.application
    carpeta = valor(app, "SELECT CAST(SERVERPROPERTY('InstanceDefaultBackupPath') AS NVARCHAR(260))")
    respuesta = enviar(
        admin,
        "/respaldos/generar",
        {"tipo": "COMPLETO", "carpeta": r"\\servidor-externo\compartida", "verificar": "0"},
    )
    assert "Respaldo generado" in texto(respuesta)
    archivo = _ultimo_respaldo(app)[4]
    assert archivo.startswith(carpeta.rstrip("\\/"))
    assert "servidor-externo" not in archivo
    assert 'name="carpeta"' not in texto(admin.get("/respaldos"))


def prueba_tipo_invalido(admin):
    respuesta = enviar(admin, "/respaldos/generar", {"tipo": "PARCIAL"})
    assert "Seleccione un tipo de respaldo válido." in texto(respuesta)


def prueba_historial_de_respaldos_no_se_puede_borrar(app):
    with app.app_context():
        with pytest.raises(DBAPIError):
            db.session.execute(text("DELETE FROM TblHistorialRespaldos"))
        db.session.rollback()


def prueba_respaldos_requiere_permiso(admin, app):
    correo = crear_usuario(admin, rol="Cajero", password="Clave_Segura_1")
    cajero = app.test_client()
    iniciar_sesion(cajero, correo, "Clave_Segura_1")
    assert cajero.get("/respaldos").status_code == 403
    assert enviar(cajero, "/respaldos/generar", {"tipo": "COMPLETO"}, seguir=False).status_code == 403
