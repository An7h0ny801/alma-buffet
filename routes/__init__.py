from routes.autenticacion import autenticacion_bp
from routes.bitacoras import bitacoras_bp
from routes.clientes import clientes_bp
from routes.cocina import cocina_bp
from routes.empleados import empleados_bp
from routes.mesas import mesas_bp
from routes.panel import panel_bp
from routes.productos import productos_bp
from routes.reportes import reportes_bp
from routes.reservaciones import reservaciones_bp
from routes.respaldos import respaldos_bp
from routes.roles import roles_bp
from routes.salud import salud_bp
from routes.tickets import tickets_bp
from routes.usuarios import usuarios_bp


BLUEPRINTS = (
    salud_bp,
    autenticacion_bp,
    panel_bp,
    tickets_bp,
    cocina_bp,
    productos_bp,
    mesas_bp,
    clientes_bp,
    reservaciones_bp,
    empleados_bp,
    usuarios_bp,
    roles_bp,
    bitacoras_bp,
    reportes_bp,
    respaldos_bp,
)
