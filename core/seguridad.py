import hashlib
import hmac
import secrets
import time
from functools import wraps

from flask import abort, current_app, g, redirect, request, session, url_for


CAMPO_CSRF = "_token_csrf"
CLAVE_USUARIO = "usuario_id"
CLAVE_HUELLA = "huella"
CLAVE_ACTIVIDAD = "ultima_actividad"
METODOS_CON_EFECTOS = {"POST", "PUT", "PATCH", "DELETE"}
INTERVALO_ACTUALIZAR_ACTIVIDAD = 60


def login_requerido(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if not g.get("usuario"):
            return redirect(url_for("autenticacion.login"))
        return vista(*args, **kwargs)

    return envoltura


def usuario_puede(permiso):
    usuario = g.get("usuario")
    return bool(usuario and usuario.tiene_permiso(permiso))


def permiso_requerido(*permisos):
    def decorador(vista):
        @wraps(vista)
        @login_requerido
        def envoltura(*args, **kwargs):
            if not all(usuario_puede(permiso) for permiso in permisos):
                abort(403)
            return vista(*args, **kwargs)

        return envoltura

    return decorador


def algun_permiso_requerido(*permisos):
    def decorador(vista):
        @wraps(vista)
        @login_requerido
        def envoltura(*args, **kwargs):
            if not any(usuario_puede(permiso) for permiso in permisos):
                abort(403)
            return vista(*args, **kwargs)

        return envoltura

    return decorador


def huella_sesion(usuario):
    clave = current_app.secret_key.encode("utf-8")
    contenido = f"{usuario.id_usuario}:{usuario.password_hash}".encode("utf-8")
    return hmac.new(clave, contenido, hashlib.sha256).hexdigest()[:32]


def iniciar_sesion_usuario(usuario):
    session.clear()
    session.permanent = True
    session[CLAVE_USUARIO] = usuario.id_usuario
    session[CLAVE_HUELLA] = huella_sesion(usuario)
    session[CLAVE_ACTIVIDAD] = int(time.time())


def renovar_huella(usuario):
    if session.get(CLAVE_USUARIO) == usuario.id_usuario:
        session[CLAVE_HUELLA] = huella_sesion(usuario)


def sesion_vigente(usuario):
    if not usuario or not usuario.activo or not usuario.empleado or not usuario.empleado.activo:
        return False, False
    if not hmac.compare_digest(session.get(CLAVE_HUELLA, ""), huella_sesion(usuario)):
        return False, False
    ahora = int(time.time())
    limite = current_app.config["SESION_INACTIVIDAD_MINUTOS"] * 60
    ultima = session.get(CLAVE_ACTIVIDAD, 0)
    if limite and ahora - ultima > limite:
        return False, True
    if ahora - ultima >= INTERVALO_ACTUALIZAR_ACTIVIDAD:
        session[CLAVE_ACTIVIDAD] = ahora
    return True, False


def obtener_token_csrf():
    token = session.get(CAMPO_CSRF)
    if not token:
        token = secrets.token_urlsafe(32)
        session[CAMPO_CSRF] = token
    return token


def validar_csrf():
    if request.method not in METODOS_CON_EFECTOS:
        return
    esperado = session.get(CAMPO_CSRF, "")
    recibido = request.form.get(CAMPO_CSRF) or request.headers.get("X-CSRF-Token", "")
    if not esperado or not recibido or not hmac.compare_digest(esperado, recibido):
        abort(400, description="La solicitud no contiene un token de seguridad válido.")


def nonce_csp():
    if "nonce_csp" not in g:
        g.nonce_csp = secrets.token_urlsafe(16)
    return g.nonce_csp


def aplicar_cabeceras_seguridad(respuesta):
    politica = (
        "default-src 'self'; "
        f"script-src 'self' 'nonce-{nonce_csp()}'; "
        "style-src 'self'; style-src-attr 'unsafe-inline'; "
        "img-src 'self' data:; font-src 'self'; connect-src 'self'; "
        "object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
    )
    cabeceras = respuesta.headers
    cabeceras.setdefault("Content-Security-Policy", politica)
    cabeceras.setdefault("X-Content-Type-Options", "nosniff")
    cabeceras.setdefault("X-Frame-Options", "DENY")
    cabeceras.setdefault("Referrer-Policy", "same-origin")
    cabeceras.setdefault("Cross-Origin-Opener-Policy", "same-origin")
    cabeceras.setdefault("Cross-Origin-Resource-Policy", "same-origin")
    cabeceras.setdefault(
        "Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=(), usb=()"
    )
    if current_app.config.get("HSTS"):
        cabeceras.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    if request.endpoint != "static":
        cabeceras["Cache-Control"] = "no-store"
        cabeceras["Pragma"] = "no-cache"
    return respuesta
