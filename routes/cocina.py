from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from models import Produccion, Producto
from core.seguridad import permiso_requerido
from services.inventario import productos_bajo_stock
from services.inventario import registrar_produccion as registrar_produccion_producto
from services.validaciones import convertir_entero_positivo


cocina_bp = Blueprint("cocina", __name__)


@cocina_bp.route("/cocina")
@permiso_requerido("cocina.ver")
def inicio():
    return render_template(
        "cocina.html",
        alertas=productos_bajo_stock(),
        productos=Producto.query.filter_by(activo=True).order_by(Producto.nombre).all(),
        producciones=Produccion.query.order_by(Produccion.id_produccion.desc())
        .limit(30)
        .all(),
    )


@cocina_bp.post("/produccion")
@permiso_requerido("cocina.gestionar")
def registrar_produccion():
    try:
        cantidad = convertir_entero_positivo(
            request.form.get("cantidad"),
            "La cantidad producida",
        )
        producto = registrar_produccion_producto(
            request.form.get("id_producto", type=int),
            cantidad,
            g.usuario.id_empleado if g.usuario else None,
        )
        flash(f"Se agregaron {cantidad} unidades de {producto.nombre}.", "success")
    except ValueError as error:
        flash(str(error), "danger")
    return redirect(url_for("cocina.inicio"))
