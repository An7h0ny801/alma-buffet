from sqlalchemy import text

import re

from core.base_datos import db
from core.migraciones import migraciones_disponibles
from tests.utilidades import consulta, crear_producto, enviar, valor


def triggers_esperados():
    patron = re.compile(r"CREATE OR ALTER TRIGGER\s+(?:\[dbo\]\.|dbo\.)?\[?(\w+)\]?")
    return {
        nombre
        for migracion in migraciones_disponibles()
        for nombre in patron.findall(migracion.contenido)
    }


def _historial_producto(app, id_producto):
    return consulta(
        app,
        "SELECT accion, idEmpleado FROM TblHistorialProductos "
        "WHERE idProducto = :p ORDER BY idHistorialProducto",
        p=id_producto,
    )


def prueba_todos_los_triggers_estan_instalados(app):
    instalados = {fila[0] for fila in consulta(app, "SELECT name FROM sys.triggers")}
    assert len(triggers_esperados()) == 28
    assert triggers_esperados() <= instalados


def prueba_cargar_el_script_no_duplica_el_historial(app):
    altas_migradas = valor(
        app,
        "SELECT COUNT(*) FROM TblHistorialProductos "
        "WHERE idProducto BETWEEN 38 AND 57 AND accion = 'INSERT'",
    )
    assert altas_migradas == 20


def prueba_cambio_desde_la_app_se_registra_una_vez_con_su_empleado(admin):
    app = admin.application
    id_producto = crear_producto(admin, stock=5)
    enviar(admin, "/produccion", {"id_producto": str(id_producto), "cantidad": "2"})
    id_empleado_admin = valor(
        app, "SELECT idEmpleado FROM TblUsuarios WHERE correo = 'admin@alma.com'"
    )
    assert _historial_producto(app, id_producto) == [
        ("INSERT", id_empleado_admin),
        ("UPDATE", id_empleado_admin),
    ]


def prueba_cambio_fuera_de_la_app_queda_a_nombre_de_sistema(admin):
    app = admin.application
    id_producto = crear_producto(admin, stock=5)
    with app.app_context():
        db.session.execute(
            text("UPDATE TblProductos SET stockUnidades = 9 WHERE idProducto = :p"),
            {"p": id_producto},
        )
        db.session.commit()
    id_sistema = valor(app, "SELECT idEmpleado FROM TblEmpleados WHERE esSistema = 1")
    assert _historial_producto(app, id_producto)[-1] == ("UPDATE", id_sistema)

