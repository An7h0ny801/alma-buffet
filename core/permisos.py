PERMISOS = (
    ("mostrador.ver", "Ver mostrador"),
    ("mostrador.gestionar", "Crear y anular tickets"),
    ("caja.ver", "Ver caja"),
    ("caja.gestionar", "Cobrar tickets y liberar mesas"),
    ("cocina.ver", "Ver cocina e inventario"),
    ("cocina.gestionar", "Registrar producción y reposición"),
    ("productos.ver", "Ver productos"),
    ("productos.gestionar", "Administrar productos"),
    ("mesas.ver", "Ver mesas"),
    ("mesas.gestionar", "Administrar mesas"),
    ("clientes.ver", "Ver clientes"),
    ("clientes.gestionar", "Administrar clientes"),
    ("reservaciones.ver", "Ver reservaciones"),
    ("reservaciones.gestionar", "Administrar reservaciones"),
    ("empleados.ver", "Ver empleados"),
    ("empleados.gestionar", "Administrar empleados"),
    ("usuarios.gestionar", "Administrar usuarios"),
    ("roles.gestionar", "Administrar roles y permisos"),
    ("bitacoras.ver", "Ver bitácoras"),
    ("reportes.ver", "Ver reportes"),
    ("respaldos.ver", "Ver historial de respaldos"),
    ("respaldos.gestionar", "Generar respaldos de la base"),
)

MODULOS = {
    "mostrador": ("Mostrador", "bi-basket2"),
    "caja": ("Caja", "bi-cash-coin"),
    "cocina": ("Cocina e inventario", "bi-bell"),
    "productos": ("Productos", "bi-box-seam"),
    "mesas": ("Mesas", "bi-grid-3x3-gap"),
    "clientes": ("Clientes", "bi-people"),
    "reservaciones": ("Reservaciones", "bi-calendar-check"),
    "empleados": ("Empleados", "bi-person-badge"),
    "usuarios": ("Usuarios", "bi-person-lock"),
    "roles": ("Roles y permisos", "bi-shield-check"),
    "bitacoras": ("Bitácoras", "bi-clock-history"),
    "reportes": ("Reportes", "bi-bar-chart"),
    "respaldos": ("Respaldos", "bi-database-down"),
}

def modulo_de(codigo):
    return codigo.split(".", 1)[0]


def accion_de(codigo):
    return codigo.split(".", 1)[-1]


def completar_dependencias(codigos):
    codigos = set(codigos)
    existentes = {codigo for codigo, _ in PERMISOS}
    for codigo in list(codigos):
        if accion_de(codigo) == "gestionar":
            ver = f"{modulo_de(codigo)}.ver"
            if ver in existentes:
                codigos.add(ver)
    return codigos

ROL_ADMINISTRADOR = "Administrador"

ROLES_BASE = {
    ROL_ADMINISTRADOR: None,
    "Mostrador": (
        "mostrador.ver",
        "mostrador.gestionar",
        "productos.ver",
        "mesas.ver",
        "mesas.gestionar",
        "clientes.ver",
        "clientes.gestionar",
        "reservaciones.ver",
        "reservaciones.gestionar",
    ),
    "Cajero": (
        "mostrador.ver",
        "mostrador.gestionar",
        "caja.ver",
        "caja.gestionar",
        "mesas.ver",
        "mesas.gestionar",
        "clientes.ver",
        "clientes.gestionar",
        "reservaciones.ver",
        "reservaciones.gestionar",
        "reportes.ver",
    ),
    "Cocinero": (
        "cocina.ver",
        "cocina.gestionar",
        "productos.ver",
        "productos.gestionar",
    ),
}
