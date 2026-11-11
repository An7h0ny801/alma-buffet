import pytest

from core import migraciones
from tests.conftest import BASE_PRUEBAS
from tests.utilidades import valor


PAGINAS = [
    "/dashboard",
    "/tickets",
    "/caja",
    "/cocina",
    "/productos",
    "/productos/nuevo",
    "/productos/38/editar",
    "/mesas",
    "/clientes",
    "/reservaciones",
    "/empleados",
    "/usuarios",
    "/roles",
    "/bitacoras",
    "/bitacoras/tickets/16",
    "/reportes",
    "/respaldos",
    "/factura/16",
]


@pytest.mark.parametrize("url", PAGINAS)
def prueba_pagina_carga(admin, url):
    assert admin.get(url).status_code == 200


def prueba_recurso_inexistente(admin):
    assert admin.get("/productos/999999/editar").status_code == 404


def prueba_migrar_de_nuevo_no_duplica_el_catalogo(app):
    tablas = ("TblPermisos", "TblRoles", "TblRolesPermisos", "TblEmpleados", "TblUsuarios")
    antes = {tabla: valor(app, f"SELECT COUNT(*) FROM {tabla}") for tabla in tablas}
    migraciones.aplicar_migraciones(BASE_PRUEBAS)
    despues = {tabla: valor(app, f"SELECT COUNT(*) FROM {tabla}") for tabla in tablas}
    assert antes == despues
