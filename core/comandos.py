import os
import sys

import click
import pyodbc
from flask.cli import with_appcontext

from core import migraciones
from core.administrador import (
    NOMBRE_PREDETERMINADO,
    AdministradorExistente,
    existe_administrador,
    inicializar_administrador,
    restablecer_administrador,
)
from core.configuracion import ConfiguracionInvalida


def _consola_interactiva():
    return sys.stdin.isatty()


def _pedir_password(etiqueta="Contraseña"):
    return click.prompt(etiqueta, hide_input=True, confirmation_prompt="Repita la contraseña")


@click.command("migrar")
@click.option("--crear-base", is_flag=True, help="Crea la base local si no existe (solo desarrollo).")
def migrar(crear_base):
    try:
        if crear_base and migraciones.crear_base_si_falta():
            click.echo("Base de datos creada.")
        resultado = migraciones.aplicar_migraciones()
        intercalacion = migraciones.intercalacion_base()
    except (migraciones.ErrorMigracion, ConfiguracionInvalida, pyodbc.Error) as error:
        raise click.ClickException(str(error)) from error
    for nombre in resultado["adoptadas"]:
        click.echo(f"Esquema existente reconocido: {nombre}")
    for nombre in resultado["aplicadas"]:
        click.echo(f"Migración aplicada: {nombre}")
    if not resultado["adoptadas"] and not resultado["aplicadas"]:
        click.echo("La base de datos ya está actualizada.")
    if intercalacion != migraciones.INTERCALACION:
        click.echo(
            f"Aviso: la base usa la intercalación {intercalacion}; "
            f"se recomienda {migraciones.INTERCALACION}.",
            err=True,
        )


@click.command("inicializar-admin")
@click.option("--si-falta", is_flag=True, help="Solo avisa si no hay datos para crear el administrador.")
@with_appcontext
def inicializar_admin(si_falta):
    if existe_administrador():
        click.echo("Ya existe un administrador; no se realizaron cambios.")
        if os.getenv("ADMIN_PASSWORD"):
            click.echo("Aviso: elimine ADMIN_PASSWORD de las variables de entorno.", err=True)
        return
    correo = os.getenv("ADMIN_CORREO", "").strip()
    password = os.getenv("ADMIN_PASSWORD", "")
    nombre = os.getenv("ADMIN_NOMBRE", "").strip() or NOMBRE_PREDETERMINADO
    desde_entorno = bool(correo and password)
    if not desde_entorno:
        if not _consola_interactiva():
            mensaje = (
                "No hay ningún administrador. Defina ADMIN_CORREO y ADMIN_PASSWORD "
                "o ejecute este comando en una consola."
            )
            if si_falta:
                click.echo(f"Aviso: {mensaje}", err=True)
                return
            raise click.ClickException(mensaje)
        click.echo(
            "La contraseña debe tener al menos 8 caracteres, con mayúscula, minúscula, número y símbolo."
        )
        correo = click.prompt("Correo del administrador").strip()
        nombre = click.prompt("Nombre completo", default=NOMBRE_PREDETERMINADO)
        password = _pedir_password()
    try:
        usuario = inicializar_administrador(
            correo, password, nombre, debe_cambiar_password=desde_entorno
        )
    except AdministradorExistente as error:
        click.echo(str(error))
        return
    except (ValueError, LookupError) as error:
        raise click.ClickException(str(error)) from error
    click.echo(f"Administrador creado: {usuario.correo}")
    if desde_entorno:
        click.echo(
            "Deberá cambiar la contraseña al iniciar sesión. "
            "Después elimine ADMIN_PASSWORD de las variables de entorno."
        )


@click.command("restablecer-admin")
@click.option("--correo", required=True, help="Correo del administrador.")
@with_appcontext
def restablecer_admin(correo):
    if not _consola_interactiva():
        raise click.ClickException("Este comando solo se puede ejecutar en una consola interactiva.")
    try:
        usuario = restablecer_administrador(correo, _pedir_password("Nueva contraseña"))
    except (ValueError, LookupError) as error:
        raise click.ClickException(str(error)) from error
    click.echo(f"Contraseña restablecida para {usuario.correo}.")


@click.command("crear-usuario-bd")
@click.option(
    "--usuario",
    default="alma_app",
    show_default=True,
    help="Usuario de base de datos que usará la aplicación.",
)
def crear_usuario_bd(usuario):
    from core.usuario_bd import crear_usuario_aplicacion

    if not _consola_interactiva():
        raise click.ClickException("Este comando solo se puede ejecutar en una consola interactiva.")
    try:
        motor = crear_usuario_aplicacion(
            usuario, _pedir_password("Contraseña del usuario de base de datos")
        )
    except (ValueError, ConfiguracionInvalida, pyodbc.Error) as error:
        raise click.ClickException(str(error)) from error
    click.echo(f"Usuario {usuario} listo en {motor} con permisos mínimos.")


COMANDOS = (migrar, inicializar_admin, restablecer_admin, crear_usuario_bd)
