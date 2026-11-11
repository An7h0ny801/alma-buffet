from datetime import date, time
from decimal import Decimal

import pytest

from services import validaciones as v


def prueba_entero_positivo():
    assert v.convertir_entero_positivo("5", "La cantidad") == 5
    with pytest.raises(ValueError, match="mayor que cero"):
        v.convertir_entero_positivo("0", "La cantidad")
    with pytest.raises(ValueError, match="número entero"):
        v.convertir_entero_positivo("abc", "La cantidad")


def prueba_monto():
    assert v.convertir_monto("1500.5") == Decimal("1500.50")
    with pytest.raises(ValueError, match="negativo"):
        v.convertir_monto("-1")
    with pytest.raises(ValueError, match="no es válido"):
        v.convertir_monto("mil")


def prueba_fecha_y_hora():
    assert v.convertir_fecha("2026-10-06", "La fecha") == date(2026, 10, 6)
    assert v.convertir_hora("19:30", "La hora") == time(19, 30)
    with pytest.raises(ValueError):
        v.convertir_fecha("06/10/2026", "La fecha")


def prueba_nombres():
    assert v.validar_nombre("  María José ") == "María José"
    with pytest.raises(ValueError):
        v.validar_nombre("Juan123")
    assert v.validar_nombre_producto("Coca-Cola 600 ml") == "Coca-Cola 600 ml"
    with pytest.raises(ValueError):
        v.validar_nombre_producto("Producto <script>")
    with pytest.raises(ValueError):
        v.validar_nombre_rol("Rol 1")


def prueba_telefono_y_correo():
    assert v.validar_telefono("88887777") == "88887777"
    assert v.validar_telefono("") is None
    with pytest.raises(ValueError, match="8 números"):
        v.validar_telefono("8888")
    assert v.validar_correo(" Ana@Alma.com ") == "ana@alma.com"
    with pytest.raises(ValueError):
        v.validar_correo("ana@alma")


def prueba_password():
    assert v.validar_password("Segura1*") == "Segura1*"
    for debil in ("corta1*", "sinmayuscula1*", "SINMINUSCULA1*", "SinNumero*", "SinSimbolo1"):
        with pytest.raises(ValueError):
            v.validar_password(debil)
