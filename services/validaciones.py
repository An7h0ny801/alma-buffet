import re
from datetime import datetime
from decimal import Decimal, InvalidOperation


PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' -]+$")
PATRON_ROL = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]+$")
PATRON_PRODUCTO = re.compile(r"^[A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ .,'()/%+-]+$")
PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def convertir_entero_positivo(valor, campo):
    try:
        numero = int(valor)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{campo} debe ser un número entero.") from error
    if numero <= 0:
        raise ValueError(f"{campo} debe ser mayor que cero.")
    return numero


def convertir_monto(valor, campo="El precio"):
    try:
        monto = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError(f"{campo} no es válido.") from error
    if monto < 0:
        raise ValueError(f"{campo} no puede ser negativo.")
    return monto.quantize(Decimal("0.01"))


def convertir_fecha(valor, campo):
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except (TypeError, ValueError) as error:
        raise ValueError(f"{campo} no es válida.") from error


def convertir_hora(valor, campo):
    try:
        return datetime.strptime(valor, "%H:%M").time()
    except (TypeError, ValueError) as error:
        raise ValueError(f"{campo} no es válida.") from error


def validar_nombre(valor, campo="El nombre"):
    valor = (valor or "").strip()
    if len(valor) > 100:
        raise ValueError(f"{campo} no puede superar 100 caracteres.")
    if not valor or not PATRON_NOMBRE.fullmatch(valor):
        raise ValueError(
            f"{campo} solo puede contener letras, espacios, guiones y apóstrofos."
        )
    return valor


def validar_nombre_rol(valor):
    valor = (valor or "").strip()
    if len(valor) > 30:
        raise ValueError("El rol no puede superar 30 caracteres.")
    if not valor or not PATRON_ROL.fullmatch(valor):
        raise ValueError("El rol solo puede contener letras y espacios.")
    return valor


def validar_nombre_producto(valor):
    valor = (valor or "").strip()
    if len(valor) > 100:
        raise ValueError("El producto no puede superar 100 caracteres.")
    if not valor or not PATRON_PRODUCTO.fullmatch(valor):
        raise ValueError("El producto contiene caracteres no permitidos.")
    return valor


def validar_telefono(valor):
    valor = (valor or "").strip()
    if valor and not re.fullmatch(r"\d{8}", valor):
        raise ValueError("El teléfono debe contener exactamente 8 números.")
    return valor or None


def validar_correo(valor):
    valor = (valor or "").strip().lower()
    if len(valor) > 120:
        raise ValueError("El correo no puede superar 120 caracteres.")
    if not PATRON_CORREO.fullmatch(valor):
        raise ValueError("El correo electrónico no es válido.")
    return valor


def validar_password(valor):
    if len(valor or "") < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres.")
    requisitos = [
        re.search(r"[A-Z]", valor),
        re.search(r"[a-z]", valor),
        re.search(r"\d", valor),
        re.search(r"[^A-Za-z0-9]", valor),
    ]
    if not all(requisitos):
        raise ValueError(
            "La contraseña debe incluir mayúscula, minúscula, número y símbolo."
        )
    return valor
