import random
import secrets
import string

from sqlalchemy import text

from core.base_datos import db
from core.seguridad import CAMPO_CSRF


TOKEN_PRUEBAS = "token-de-pruebas"
CORREO_ADMIN = "admin@alma.com"
PASSWORD_ADMIN = "Pr" + secrets.token_urlsafe(12) + "9*"


def _asegurar_token(cliente_http):
    with cliente_http.session_transaction() as sesion:
        sesion.setdefault(CAMPO_CSRF, TOKEN_PRUEBAS)
        return sesion[CAMPO_CSRF]


def enviar(cliente_http, url, datos=None, seguir=True):
    datos = dict(datos or {})
    datos[CAMPO_CSRF] = _asegurar_token(cliente_http)
    return cliente_http.post(url, data=datos, follow_redirects=seguir)


def iniciar_sesion(cliente_http, correo, password):
    return enviar(
        cliente_http,
        "/validar_login",
        {"correo": correo, "password": password},
        seguir=False,
    )


def texto(respuesta):
    return respuesta.get_data(as_text=True)


def consulta(app, sql, **parametros):
    with app.app_context():
        return db.session.execute(text(sql), parametros).all()


def valor(app, sql, **parametros):
    return consulta(app, sql, **parametros)[0][0]


def nombre_unico(prefijo):
    sufijo = "".join(random.choices(string.ascii_lowercase, k=8))
    return f"{prefijo} {sufijo}"


def numero_unico():
    return random.randint(1000, 999999)


def crear_producto(admin, *, precio="1500", stock=20, unidad="Porción", nombre=None):
    nombre = nombre or nombre_unico("Producto")
    enviar(
        admin,
        "/productos/guardar",
        {
            "nombre": nombre,
            "precio_unidad": precio,
            "unidad_medida": unidad,
            "stock_unidades": str(stock),
            "activo": "1",
        },
    )
    return valor(admin.application, "SELECT idProducto FROM TblProductos WHERE nombre = :n", n=nombre)


def crear_mesa(admin, capacidad=4):
    numero = numero_unico()
    enviar(admin, "/mesas/guardar", {"numero_mesa": str(numero), "capacidad": str(capacidad)})
    return valor(admin.application, "SELECT idMesa FROM TblMesas WHERE numeroMesa = :n", n=numero)


def crear_cliente(admin):
    nombre = nombre_unico("Cliente")
    enviar(admin, "/clientes/guardar", {"nombre": nombre, "telefono": "88881111"})
    return valor(admin.application, "SELECT idCliente FROM TblClientes WHERE nombre = :n", n=nombre)


def crear_ticket(admin, cantidades):
    enviar(
        admin,
        "/tickets/enviar",
        {f"cantidad_{id_producto}": str(cantidad) for id_producto, cantidad in cantidades.items()},
    )
    return valor(admin.application, "SELECT MAX(idTicket) FROM TblTickets")


def crear_usuario(admin, *, rol, password, debe_cambiar=False):
    nombre = nombre_unico("Empleado")
    enviar(
        admin,
        "/empleados/guardar",
        {
            "nombre": nombre,
            "puesto": "Cajero",
            "telefono": "88887777",
            "fecha_contratacion": "2026-01-10",
            "activo": "1",
        },
    )
    app = admin.application
    id_empleado = valor(app, "SELECT idEmpleado FROM TblEmpleados WHERE nombre = :n", n=nombre)
    id_rol = valor(app, "SELECT idRol FROM TblRoles WHERE nombre = :r", r=rol)
    correo = f"u{numero_unico()}@alma.com"
    datos = {
        "correo": correo,
        "id_rol": str(id_rol),
        "id_empleado": str(id_empleado),
        "activo": "1",
        "password": password,
    }
    if debe_cambiar:
        datos["debe_cambiar_password"] = "1"
    enviar(admin, "/usuarios/guardar", datos)
    return correo
