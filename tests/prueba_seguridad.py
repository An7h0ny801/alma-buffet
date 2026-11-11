import re
import time
from pathlib import Path

import pytest
from werkzeug.security import generate_password_hash

from core.seguridad import CAMPO_CSRF, CLAVE_ACTIVIDAD
from tests.utilidades import (
    CORREO_ADMIN,
    PASSWORD_ADMIN,
    consulta,
    crear_usuario,
    enviar,
    iniciar_sesion,
    nombre_unico,
    texto,
    valor,
)


RAIZ = Path(__file__).resolve().parent.parent


def _crear_rol(admin, permisos):
    nombre = nombre_unico("Encargado")
    enviar(admin, "/roles/guardar", {"nombre": nombre, "permisos": permisos})
    return nombre, valor(admin.application, "SELECT idRol FROM TblRoles WHERE nombre = :n", n=nombre)


def _sesion(app, correo, password):
    cliente_http = app.test_client()
    respuesta = iniciar_sesion(cliente_http, correo, password)
    assert respuesta.status_code == 302
    return cliente_http


def _id_usuario(app, correo):
    return valor(app, "SELECT idUsuario FROM TblUsuarios WHERE correo = :c", c=correo)


def _datos_usuario(app, correo, **cambios):
    fila = consulta(
        app,
        "SELECT idUsuario, correo, idRol, idEmpleado FROM TblUsuarios WHERE correo = :c",
        c=correo,
    )[0]
    datos = {
        "id_usuario": str(fila.idUsuario),
        "correo": fila.correo,
        "id_rol": str(fila.idRol),
        "id_empleado": str(fila.idEmpleado),
        "activo": "1",
    }
    datos.update(cambios)
    return datos


def prueba_cabeceras_de_seguridad_y_nonce(cliente):
    respuesta = cliente.get("/login")
    cabeceras = respuesta.headers
    politica = cabeceras["Content-Security-Policy"]
    nonce = re.search(r"'nonce-([^']+)'", politica).group(1)
    assert f'nonce="{nonce}"' in texto(respuesta)
    assert "frame-ancestors 'none'" in politica and "object-src 'none'" in politica
    assert cabeceras["X-Frame-Options"] == "DENY"
    assert cabeceras["X-Content-Type-Options"] == "nosniff"
    assert cabeceras["Referrer-Policy"] == "same-origin"
    assert cabeceras["Cache-Control"] == "no-store"
    assert "Access-Control-Allow-Origin" not in cabeceras
    assert cliente.get("/login").headers["Content-Security-Policy"] != politica


def prueba_plantillas_sin_javascript_en_linea():
    for ruta in (RAIZ / "templates").glob("*.html"):
        contenido = ruta.read_text(encoding="utf-8")
        assert not re.search(r"\son[a-z]+\s*=", contenido), ruta.name
        assert "<script>" not in contenido, ruta.name
        assert "|safe" not in contenido, ruta.name


def prueba_salud_no_requiere_sesion_ni_base(cliente):
    respuesta = cliente.get("/salud")
    assert respuesta.status_code == 200
    assert respuesta.get_json() == {"estado": "ok"}


def prueba_errores_en_espanol_sin_detalles_internos(admin, cliente):
    respuesta = admin.get("/no-existe")
    assert respuesta.status_code == 404
    assert "No se encontró el recurso solicitado." in texto(respuesta)
    assert cliente.get("/validar_login").status_code == 405
    assert "Traceback" not in texto(cliente.get("/validar_login"))


def prueba_usuario_inexistente_recibe_el_mismo_mensaje(cliente):
    respuesta = enviar(cliente, "/validar_login", {"correo": "nadie@alma.com", "password": "x"})
    assert "Correo o contraseña incorrectos." in texto(respuesta)


def prueba_bloqueo_por_intentos_fallidos(app, admin):
    correo = crear_usuario(admin, rol="Cajero", password="Bloqueo1*Clave")
    cliente_http = app.test_client()
    for _ in range(app.config["LOGIN_MAX_INTENTOS"]):
        enviar(cliente_http, "/validar_login", {"correo": correo, "password": "Incorrecta1*"})
    respuesta = enviar(cliente_http, "/validar_login", {"correo": correo, "password": "Bloqueo1*Clave"})
    assert "Demasiados intentos fallidos" in texto(respuesta)
    assert cliente_http.get("/dashboard").status_code == 302


def prueba_bloqueo_por_direccion_ip(app, admin):
    correo = crear_usuario(admin, rol="Cajero", password="PorIp1*Clave")
    anterior = app.config["LOGIN_MAX_INTENTOS_IP"]
    fallidos = valor(
        app,
        "SELECT COUNT(*) FROM TblAuditoriaSesiones WHERE direccionIp = '127.0.0.1' "
        "AND evento = 'LOGIN_FALLIDO' AND fechaHora >= DATEADD(MINUTE, -15, SYSDATETIME())",
    )
    app.config["LOGIN_MAX_INTENTOS_IP"] = fallidos + 1
    try:
        cliente_http = app.test_client()
        enviar(cliente_http, "/validar_login", {"correo": nombre_unico("x") + "@alma.com", "password": "x"})
        respuesta = enviar(cliente_http, "/validar_login", {"correo": correo, "password": "PorIp1*Clave"})
        assert "Demasiados intentos fallidos" in texto(respuesta)
    finally:
        app.config["LOGIN_MAX_INTENTOS_IP"] = anterior


def prueba_contrasenas_nuevas_usan_argon2id(app, admin):
    correo = crear_usuario(admin, rol="Cajero", password="Argon2*Clave")
    hash_guardado = valor(app, "SELECT passwordHash FROM TblUsuarios WHERE correo = :c", c=correo)
    assert hash_guardado.startswith("$argon2id$")


def prueba_hash_antiguo_se_actualiza_al_iniciar_sesion(app, admin):
    correo = crear_usuario(admin, rol="Cajero", password="Antigua1*Clave")
    from sqlalchemy import text

    from core.base_datos import db

    with app.app_context():
        db.session.execute(
            text("UPDATE TblUsuarios SET passwordHash = :h WHERE correo = :c"),
            {"h": generate_password_hash("Antigua1*Clave"), "c": correo},
        )
        db.session.commit()
    _sesion(app, correo, "Antigua1*Clave")
    hash_guardado = valor(app, "SELECT passwordHash FROM TblUsuarios WHERE correo = :c", c=correo)
    assert hash_guardado.startswith("$argon2id$")


def prueba_cambiar_la_contrasena_cierra_las_otras_sesiones(app, admin):
    correo = crear_usuario(admin, rol="Cajero", password="Primera1*Clave")
    primera = _sesion(app, correo, "Primera1*Clave")
    segunda = _sesion(app, correo, "Primera1*Clave")
    respuesta = enviar(
        segunda,
        "/cambiar-password",
        {
            "password_actual": "Primera1*Clave",
            "password_nueva": "Segunda2*Clave",
            "password_confirmacion": "Segunda2*Clave",
        },
    )
    assert "Contraseña actualizada." in texto(respuesta)
    assert segunda.get("/caja").status_code == 200
    assert "/login" in primera.get("/caja").location


def prueba_restablecer_desde_usuarios_cierra_la_sesion_del_afectado(app, admin):
    correo = crear_usuario(admin, rol="Cajero", password="Afectado1*Clave")
    afectado = _sesion(app, correo, "Afectado1*Clave")
    enviar(admin, "/usuarios/guardar", _datos_usuario(app, correo, password="Nueva2*Clave"))
    assert "/login" in afectado.get("/caja").location


def prueba_sesion_expira_por_inactividad(app, admin):
    correo = crear_usuario(admin, rol="Cajero", password="Inactivo1*Clave")
    cliente_http = _sesion(app, correo, "Inactivo1*Clave")
    with cliente_http.session_transaction() as sesion:
        sesion[CLAVE_ACTIVIDAD] = int(time.time()) - app.config["SESION_INACTIVIDAD_MINUTOS"] * 60 - 5
    respuesta = cliente_http.get("/caja")
    assert "/login" in respuesta.location
    assert "inactividad" in texto(cliente_http.get("/login"))


def prueba_cookie_de_sesion_protegida(cliente):
    respuesta = cliente.get("/login")
    cookie = respuesta.headers["Set-Cookie"]
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie


def prueba_gestor_de_usuarios_no_puede_escalar_privilegios(app, admin):
    _, id_rol_gestor = _crear_rol(admin, ["usuarios.gestionar", "empleados.ver"])
    correo = crear_usuario(admin, rol="Cajero", password="Gestor1*Clave")
    enviar(admin, "/usuarios/guardar", _datos_usuario(app, correo, id_rol=str(id_rol_gestor)))
    gestor = _sesion(app, correo, "Gestor1*Clave")
    id_admin_rol = valor(app, "SELECT idRol FROM TblRoles WHERE nombre = 'Administrador'")
    id_cajero = valor(app, "SELECT idRol FROM TblRoles WHERE nombre = 'Cajero'")

    respuesta = enviar(gestor, "/usuarios/guardar", _datos_usuario(app, correo, id_rol=str(id_admin_rol)))
    assert "Solo un administrador puede asignar el rol Administrador." in texto(respuesta)

    respuesta = enviar(gestor, "/usuarios/guardar", _datos_usuario(app, correo, id_rol=str(id_cajero)))
    assert "No puede asignar un rol con permisos que usted no tiene." in texto(respuesta)

    respuesta = enviar(gestor, "/usuarios/guardar", _datos_usuario(app, CORREO_ADMIN, password="Robada1*Clave"))
    assert "Solo un administrador puede modificar a otro administrador." in texto(respuesta)
    assert iniciar_sesion(app.test_client(), CORREO_ADMIN, PASSWORD_ADMIN).location.endswith("/dashboard")

    respuesta = enviar(gestor, f"/usuarios/{_id_usuario(app, CORREO_ADMIN)}/eliminar")
    assert "Solo un administrador puede modificar a otro administrador." in texto(respuesta)
    assert valor(app, "SELECT idRol FROM TblUsuarios WHERE correo = :c", c=correo) == id_rol_gestor


def prueba_gestor_de_roles_no_puede_escalar_privilegios(app, admin):
    nombre_gestor, id_rol_gestor = _crear_rol(admin, ["roles.gestionar", "caja.ver"])
    correo = crear_usuario(admin, rol="Cajero", password="Roles1*Clave")
    enviar(admin, "/usuarios/guardar", _datos_usuario(app, correo, id_rol=str(id_rol_gestor)))
    gestor = _sesion(app, correo, "Roles1*Clave")

    respuesta = enviar(gestor, f"/roles/{id_rol_gestor}/permisos", {"permisos": ["roles.gestionar", "usuarios.gestionar"]})
    assert "No puede modificar los permisos de su propio rol." in texto(respuesta)

    respuesta = enviar(gestor, "/roles/guardar", {"nombre": nombre_unico("Nuevo"), "permisos": ["respaldos.gestionar"]})
    assert "No puede otorgar permisos que usted no tiene." in texto(respuesta)

    respuesta = enviar(gestor, "/roles/guardar", {"nombre": "Administrador", "permisos": ["caja.ver"]})
    assert "reservado" in texto(respuesta)

    id_cajero = valor(app, "SELECT idRol FROM TblRoles WHERE nombre = 'Cajero'")
    respuesta = enviar(gestor, f"/roles/{id_cajero}/permisos", {"permisos": ["caja.ver"]})
    assert "No puede modificar un rol con permisos que usted no tiene." in texto(respuesta)

    nombre_nuevo = nombre_unico("Consulta")
    respuesta = enviar(gestor, "/roles/guardar", {"nombre": nombre_nuevo, "permisos": ["caja.ver"]})
    assert "Rol guardado." in texto(respuesta)
    assert valor(app, "SELECT COUNT(*) FROM TblRoles WHERE nombre = :n", n=nombre_gestor) == 1


def prueba_no_hay_registro_publico_de_usuarios(cliente):
    for ruta in ("/registro", "/registrarse", "/usuarios/registro", "/signup"):
        assert cliente.get(ruta).status_code == 404
    assert cliente.get("/usuarios").status_code == 302
    assert enviar(cliente, "/usuarios/guardar", {"correo": "x@alma.com"}, seguir=False).status_code == 302


@pytest.mark.parametrize(
    "ruta",
    ["/usuarios", "/roles", "/bitacoras", "/respaldos", "/empleados", "/reportes"],
)
def prueba_rutas_administrativas_rechazan_a_un_cajero(app, admin, ruta):
    correo = crear_usuario(admin, rol="Mostrador", password="Mostrador1*")
    mostrador = _sesion(app, correo, "Mostrador1*")
    assert mostrador.get(ruta).status_code == 403


def prueba_formulario_con_error_no_redirige_a_sitios_externos(admin):
    with admin.session_transaction() as sesion:
        token = sesion.setdefault(CAMPO_CSRF, "token-de-pruebas")
    respuesta = admin.post(
        "/productos/guardar",
        data={"nombre": "", "precio_unidad": "x", CAMPO_CSRF: token},
        headers={"Referer": "https://sitio-malicioso.example/"},
    )
    assert respuesta.status_code == 302
    assert "sitio-malicioso" not in respuesta.location


def prueba_el_codigo_no_contiene_credenciales():
    prohibidos = ("An7h0n10", "Cambie_Esta_Clave", "scrypt:32768", "PWD=", "Password=")
    carpetas = ("core", "models", "routes", "services", "templates", "static/js", "migrations", "deploy")
    archivos = [RAIZ / "run.py", RAIZ / "Dockerfile", RAIZ / "render.yaml", RAIZ / ".env.example"]
    for carpeta in carpetas:
        archivos += [ruta for ruta in (RAIZ / carpeta).rglob("*") if ruta.is_file() and ruta.suffix != ".pyc"]
    for ruta in archivos:
        contenido = ruta.read_text(encoding="utf-8", errors="ignore")
        for prohibido in prohibidos:
            if prohibido == "PWD=" and ruta.name == "configuracion.py":
                continue
            assert prohibido not in contenido, f"{prohibido} en {ruta}"
