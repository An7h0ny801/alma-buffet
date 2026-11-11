from tests.utilidades import consulta, crear_producto, enviar, nombre_unico, texto, valor


def _datos(nombre, precio="2500", stock="10", unidad="Porción", **extra):
    datos = {
        "nombre": nombre,
        "precio_unidad": precio,
        "unidad_medida": unidad,
        "stock_unidades": stock,
        "activo": "1",
    }
    datos.update(extra)
    return datos


def prueba_insertar_producto(admin):
    nombre = nombre_unico("Arroz")
    respuesta = enviar(admin, "/productos/guardar", _datos(nombre))
    assert "Producto guardado." in texto(respuesta)
    assert valor(admin.application, "SELECT COUNT(*) FROM TblProductos WHERE nombre = :n", n=nombre) == 1


def prueba_nombre_duplicado_muestra_mensaje_de_la_base(admin):
    nombre = nombre_unico("Duplicado")
    enviar(admin, "/productos/guardar", _datos(nombre))
    respuesta = enviar(admin, "/productos/guardar", _datos(nombre))
    assert "Ya existe un producto registrado con ese nombre." in texto(respuesta)


def prueba_precio_cero_rechazado_al_insertar(admin):
    respuesta = enviar(admin, "/productos/guardar", _datos(nombre_unico("Fresco"), precio="0"))
    assert "El precio del producto no puede ser menor a 0." in texto(respuesta)


def prueba_fresco_gratuito_se_logra_editando(admin):
    nombre = nombre_unico("Fresco")
    id_producto = crear_producto(admin, nombre=nombre, precio="1", unidad="Vaso")
    respuesta = enviar(
        admin,
        "/productos/guardar",
        _datos(nombre, precio="0", unidad="Vaso", id_producto=str(id_producto)),
    )
    assert "Producto guardado." in texto(respuesta)
    assert "Vaso incluido sin costo" in texto(admin.get("/productos"))


def prueba_eliminar_es_borrado_logico(admin):
    id_producto = crear_producto(admin)
    respuesta = enviar(admin, f"/productos/{id_producto}/eliminar")
    assert "Producto desactivado." in texto(respuesta)
    assert valor(admin.application, "SELECT activo FROM TblProductos WHERE idProducto = :p", p=id_producto) is False

    respuesta = enviar(admin, f"/productos/{id_producto}/eliminar")
    assert "El producto ya se encuentra inactivo." in texto(respuesta)


def prueba_bitacora_de_productos(admin):
    app = admin.application
    nombre = nombre_unico("Auditado")
    id_producto = crear_producto(admin, nombre=nombre)
    enviar(admin, "/productos/guardar", _datos(nombre, stock="7", id_producto=str(id_producto)))
    enviar(admin, f"/productos/{id_producto}/eliminar")

    filas = consulta(
        app,
        "SELECT accion, idEmpleado FROM TblHistorialProductos "
        "WHERE idProducto = :p ORDER BY idHistorialProducto",
        p=id_producto,
    )
    assert [fila[0] for fila in filas] == ["INSERT", "UPDATE", "UPDATE"]
    id_empleado_admin = valor(
        app, "SELECT idEmpleado FROM TblUsuarios WHERE correo = 'admin@alma.com'"
    )
    assert {fila[1] for fila in filas} == {id_empleado_admin}
