from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from models import Producto
from core.base_datos import db
from core.seguridad import permiso_requerido, usuario_puede
from services.productos import UNIDADES_MEDIDA, eliminar_producto, guardar_producto
from services.validaciones import convertir_monto


productos_bp = Blueprint("productos", __name__, url_prefix="/productos")


@productos_bp.route("")
@permiso_requerido("productos.ver")
def listar():
    consulta = Producto.query
    if not usuario_puede("productos.gestionar"):
        consulta = consulta.filter(Producto.activo == True)
    productos = consulta.order_by(Producto.activo.desc(), Producto.nombre).all()
    return render_template("productos.html", productos=productos)


@productos_bp.route("/nuevo")
@permiso_requerido("productos.gestionar")
def nuevo():
    return render_template(
        "producto_form.html", producto=None, unidades=UNIDADES_MEDIDA
    )


@productos_bp.route("/<int:id_producto>/editar")
@permiso_requerido("productos.gestionar")
def editar(id_producto):
    producto = db.session.get(Producto, id_producto)
    if not producto:
        abort(404)
    return render_template(
        "producto_form.html", producto=producto, unidades=UNIDADES_MEDIDA
    )


@productos_bp.post("/guardar")
@permiso_requerido("productos.gestionar")
def guardar():
    try:
        guardar_producto(
            request.form.get("id_producto", type=int),
            nombre=request.form.get("nombre", "").strip(),
            precio=convertir_monto(request.form.get("precio_unidad")),
            stock=int(request.form.get("stock_unidades", 0)),
            unidad=request.form.get("unidad_medida", ""),
            activo=request.form.get("activo") == "1",
        )
        flash("Producto guardado.", "success")
        return redirect(url_for("productos.listar"))
    except ValueError as error:
        flash(str(error), "danger")
        id_producto = request.form.get("id_producto", type=int)
        if id_producto:
            return redirect(url_for("productos.editar", id_producto=id_producto))
        return redirect(url_for("productos.nuevo"))


@productos_bp.post("/<int:id_producto>/eliminar")
@permiso_requerido("productos.gestionar")
def eliminar(id_producto):
    try:
        eliminar_producto(id_producto)
        flash("Producto desactivado.", "success")
    except ValueError as error:
        flash(str(error), "danger")
    return redirect(url_for("productos.listar"))
