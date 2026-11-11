from sqlalchemy import select

from models import Empleado, Produccion, Producto
from core.base_datos import BLOQUEO_FILA, db
from core.procedimientos import ejecutar_procedimiento


STOCK_MINIMO = 3


def productos_bajo_stock(stock_minimo=STOCK_MINIMO):
    filas = ejecutar_procedimiento("pa_ProductosBajoStock", pStockMinimo=stock_minimo)
    ids = [fila["idProducto"] for fila in filas]
    if not ids:
        return []
    productos = {
        producto.id_producto: producto
        for producto in Producto.query.filter(Producto.id_producto.in_(ids)).all()
    }
    return [productos[id_producto] for id_producto in ids if id_producto in productos]


def registrar_produccion(id_producto, cantidad, id_empleado=None):
    try:
        producto = (
            db.session.execute(
                select(Producto)
                .where(
                    Producto.id_producto == id_producto,
                    Producto.activo == True,
                )
                .with_hint(Producto, BLOQUEO_FILA, "mssql")
            )
            .scalars()
            .first()
        )
        if not producto:
            raise ValueError("Producto inválido.")
        if not id_empleado:
            empleado = Empleado.query.filter_by(activo=True).first()
            if not empleado:
                raise ValueError("Debe existir un empleado activo.")
            id_empleado = empleado.id_empleado

        producto.stock_unidades += cantidad
        db.session.add(
            Produccion(
                producto=producto,
                id_empleado=id_empleado,
                cantidad_producida_unidades=cantidad,
            )
        )
        db.session.commit()
        return producto
    except Exception:
        db.session.rollback()
        raise
