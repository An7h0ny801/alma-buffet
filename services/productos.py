from core.base_datos import db
from core.procedimientos import ejecutar_procedimiento
from services.validaciones import validar_nombre_producto


UNIDADES_MEDIDA = ("Porción", "Vaso", "Botella")


def guardar_producto(id_producto, *, nombre, precio, stock, unidad, activo):
    if unidad not in UNIDADES_MEDIDA:
        raise ValueError("La unidad de medida no es válida.")
    nombre = validar_nombre_producto(nombre)
    if stock < 0:
        raise ValueError("El inventario no puede ser negativo.")
    parametros = {
        "pNombre": nombre,
        "pPrecioUnidad": precio,
        "pUnidadMedida": unidad,
        "pStockUnidades": stock,
        "pActivo": activo,
    }
    try:
        if id_producto:
            filas = ejecutar_procedimiento(
                "pa_ProductoActualizar", pIdProducto=id_producto, **parametros
            )
        else:
            filas = ejecutar_procedimiento("pa_ProductoInsertar", **parametros)
        producto = filas[0]
        db.session.commit()
        db.session.expire_all()
        return producto
    except Exception:
        db.session.rollback()
        raise


def eliminar_producto(id_producto):
    try:
        filas = ejecutar_procedimiento("pa_ProductoEliminar", pIdProducto=id_producto)
        db.session.commit()
        db.session.expire_all()
        return filas[0]
    except Exception:
        db.session.rollback()
        raise
