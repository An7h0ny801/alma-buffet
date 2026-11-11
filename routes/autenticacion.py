from flask import Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for

from core.base_datos import db
from core.contrasenas import consumir_tiempo_de_verificacion
from core.seguridad import iniciar_sesion_usuario, login_requerido, renovar_huella
from models import Usuario
from services.acceso import cambiar_password as cambiar_password_usuario
from services.auditoria import (
    LOGIN_FALLIDO,
    LOGIN_OK,
    LOGOUT,
    login_bloqueado,
    registrar_evento_sesion,
)


autenticacion_bp = Blueprint("autenticacion", __name__)

MENSAJE_CREDENCIALES = "Correo o contraseña incorrectos."
MENSAJE_BLOQUEO = "Demasiados intentos fallidos. Espere unos minutos e inténtelo de nuevo."
LONGITUD_MAXIMA_PASSWORD = 128


def _credenciales_validas(usuario, password):
    if not usuario:
        return consumir_tiempo_de_verificacion(password)
    valida = usuario.verificar_password(password)
    return bool(valida and usuario.activo and usuario.empleado and usuario.empleado.activo)


def _actualizar_hash_si_corresponde(usuario, password):
    if not usuario.hash_desactualizado:
        return
    try:
        usuario.asignar_password(password)
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("No se pudo actualizar el hash de la contraseña.")


@autenticacion_bp.route("/")
@autenticacion_bp.route("/login")
def login():
    if g.get("usuario"):
        return redirect(url_for("panel.inicio"))
    return render_template("login.html")


@autenticacion_bp.post("/validar_login")
def validar_login():
    correo = request.form.get("correo", "").strip().lower()[:120]
    password = request.form.get("password", "")[:LONGITUD_MAXIMA_PASSWORD]

    if login_bloqueado(correo):
        registrar_evento_sesion(LOGIN_FALLIDO, correo)
        flash(MENSAJE_BLOQUEO, "danger")
        return redirect(url_for("autenticacion.login"))

    usuario = Usuario.query.filter_by(correo=correo).first() if correo else None
    if not _credenciales_validas(usuario, password):
        registrar_evento_sesion(LOGIN_FALLIDO, correo)
        flash(MENSAJE_CREDENCIALES, "danger")
        return redirect(url_for("autenticacion.login"))

    _actualizar_hash_si_corresponde(usuario, password)
    iniciar_sesion_usuario(usuario)
    registrar_evento_sesion(LOGIN_OK, usuario.correo, usuario.id_usuario)
    if usuario.debe_cambiar_password:
        return redirect(url_for("autenticacion.cambiar_password"))
    return redirect(url_for("panel.inicio"))


@autenticacion_bp.route("/cambiar-password")
@login_requerido
def cambiar_password():
    return render_template("cambiar_password.html")


@autenticacion_bp.post("/cambiar-password")
@login_requerido
def guardar_password():
    password_nueva = request.form.get("password_nueva", "")[:LONGITUD_MAXIMA_PASSWORD]
    confirmacion = request.form.get("password_confirmacion", "")[:LONGITUD_MAXIMA_PASSWORD]
    if password_nueva != confirmacion:
        flash("La confirmación de contraseña no coincide.", "danger")
        return redirect(url_for("autenticacion.cambiar_password"))
    try:
        cambiar_password_usuario(
            g.usuario,
            request.form.get("password_actual", "")[:LONGITUD_MAXIMA_PASSWORD],
            password_nueva,
        )
    except ValueError as error:
        flash(str(error), "danger")
        return redirect(url_for("autenticacion.cambiar_password"))
    renovar_huella(g.usuario)
    flash("Contraseña actualizada.", "success")
    return redirect(url_for("panel.inicio"))


@autenticacion_bp.post("/logout")
def cerrar_sesion():
    if g.get("usuario"):
        registrar_evento_sesion(LOGOUT, g.usuario.correo, g.usuario.id_usuario)
    session.clear()
    return redirect(url_for("autenticacion.login"))
