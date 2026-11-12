from datetime import timezone
from zoneinfo import ZoneInfo

from flask import Flask, current_app, flash, g, redirect, render_template, request, session, url_for
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from core.base_datos import db
from core.bitacoras import asignar_empleado_en_transaccion, registrar_contexto_empleado
from core.comandos import COMANDOS
from core.configuracion import RAIZ_PROYECTO, cargar_configuracion
from core.registro import configurar_registro
from core.seguridad import (
    CLAVE_USUARIO,
    aplicar_cabeceras_seguridad,
    nonce_csp,
    obtener_token_csrf,
    sesion_vigente,
    usuario_puede,
    validar_csrf,
)
from models import Usuario
from routes import BLUEPRINTS


ENDPOINTS_CAMBIO_PASSWORD = {
    "autenticacion.cambiar_password",
    "autenticacion.guardar_password",
    "autenticacion.cerrar_sesion",
    "salud.estado",
    "static",
}
ENDPOINTS_SIN_SESION = {"salud.estado", "static"}

MENSAJES_ERROR = {
    400: "La solicitud contiene datos inválidos.",
    403: "No tiene permisos para realizar esta acción.",
    404: "No se encontró el recurso solicitado.",
    405: "El método de la solicitud no está permitido.",
    409: "La operación entra en conflicto con el estado actual.",
    413: "La solicitud es demasiado grande.",
    500: "Ocurrió un error interno. No se guardaron cambios incompletos.",
}
MENSAJE_BD_NO_DISPONIBLE = (
    "La base de datos no está disponible en este momento. "
    "Si estaba en pausa puede tardar un minuto en reanudarse; inténtelo de nuevo."
)
MENSAJE_BD_ERROR = "Ocurrió un error con la base de datos. No se guardaron cambios incompletos."


def _hora_local(valor, formato="%d/%m/%Y %H:%M:%S"):
    if valor is None:
        return "—"
    zona_base = current_app.config.get("ZONA_HORARIA_BD")
    if zona_base and hasattr(valor, "hour"):
        origen = timezone.utc if zona_base.upper() == "UTC" else ZoneInfo(zona_base)
        valor = valor.replace(tzinfo=origen).astimezone(ZoneInfo(current_app.config["ZONA_HORARIA"]))
    return valor.strftime(formato)


def _mensaje_http(error):
    codigo = error.code or 500
    descripcion = error.description
    if codigo == 500 or descripcion == type(error).description:
        return MENSAJES_ERROR.get(codigo, MENSAJES_ERROR[500])
    return descripcion


def _pagina_error(codigo, mensaje):
    return render_template("error.html", codigo=codigo, mensaje=mensaje), codigo


def _registrar_peticiones(app):
    @app.before_request
    def cargar_usuario_y_validar_csrf():
        g.usuario = None
        if request.endpoint in ENDPOINTS_SIN_SESION:
            return None
        id_usuario = session.get(CLAVE_USUARIO)
        if id_usuario:
            usuario = db.session.get(Usuario, id_usuario)
            vigente, por_inactividad = sesion_vigente(usuario)
            if vigente:
                g.usuario = usuario
                g.id_empleado = usuario.id_empleado
                asignar_empleado_en_transaccion(db.session)
            else:
                session.clear()
                if por_inactividad:
                    flash("Su sesión se cerró por inactividad. Inicie sesión de nuevo.", "info")
        validar_csrf()
        if (
            g.usuario
            and g.usuario.debe_cambiar_password
            and request.endpoint not in ENDPOINTS_CAMBIO_PASSWORD
        ):
            return redirect(url_for("autenticacion.cambiar_password"))
        return None

    @app.after_request
    def cabeceras(respuesta):
        return aplicar_cabeceras_seguridad(respuesta)

    @app.teardown_request
    def deshacer_transaccion_fallida(error):
        if error is not None:
            db.session.rollback()

    @app.context_processor
    def variables_plantillas():
        return {
            "token_csrf": obtener_token_csrf,
            "csp_nonce": nonce_csp,
            "usuario_actual": g.get("usuario"),
            "endpoint_actual": request.endpoint or "",
            "puede": usuario_puede,
        }


def _registrar_errores(app):
    @app.errorhandler(SQLAlchemyError)
    def error_base_datos(error):
        app.logger.error("Error de base de datos: %s", type(error).__name__, exc_info=error)
        db.session.rollback()
        db.session.remove()
        if isinstance(error, OperationalError):
            return _pagina_error(503, MENSAJE_BD_NO_DISPONIBLE)
        return _pagina_error(500, MENSAJE_BD_ERROR)

    @app.errorhandler(HTTPException)
    def error_http(error):
        db.session.rollback()
        return _pagina_error(error.code or 500, _mensaje_http(error))

    @app.errorhandler(Exception)
    def error_inesperado(error):
        app.logger.exception("Error no controlado", exc_info=error)
        db.session.rollback()
        return _pagina_error(500, MENSAJES_ERROR[500])


def crear_app(configuracion_extra=None):
    app = Flask(
        __name__,
        root_path=str(RAIZ_PROYECTO),
        static_folder="static",
        template_folder="templates",
    )
    app.config.update(cargar_configuracion())
    if configuracion_extra:
        app.config.update(configuracion_extra)

    saltos = app.config["PROXY_SALTOS"]
    if saltos:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=saltos, x_proto=saltos, x_host=0, x_prefix=0)

    configurar_registro(app)
    db.init_app(app)
    registrar_contexto_empleado()
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)
    for comando in COMANDOS:
        app.cli.add_command(comando)
    app.add_template_filter(_hora_local, "hora_local")

    _registrar_peticiones(app)
    _registrar_errores(app)
    return app
