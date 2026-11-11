from tests.utilidades import crear_producto, enviar, texto, valor


def prueba_registrar_produccion(admin):
    app = admin.application
    id_producto = crear_producto(admin, stock=1)
    respuesta = enviar(admin, "/produccion", {"id_producto": str(id_producto), "cantidad": "6"})
    assert "Se agregaron 6 unidades" in texto(respuesta)
    assert valor(app, "SELECT stockUnidades FROM TblProductos WHERE idProducto = :p", p=id_producto) == 7
    assert valor(app, "SELECT COUNT(*) FROM TblProduccion WHERE idProducto = :p", p=id_producto) == 1


def prueba_alerta_de_bajo_stock(admin):
    nombre = "Producto escaso"
    crear_producto(admin, nombre=nombre, stock=2)
    assert nombre in texto(admin.get("/cocina"))
    assert nombre in texto(admin.get("/dashboard"))


def prueba_reportes_con_filtro_de_fechas(admin):
    respuesta = admin.get("/reportes?desde=2026-06-12&hasta=2026-06-12")
    assert respuesta.status_code == 200
    assert "1,130.00" in texto(respuesta)


def prueba_reporte_con_fecha_invalida(admin):
    assert admin.get("/reportes?desde=12-06-2026").status_code == 400


def prueba_reporte_de_ventas_pdf(admin):
    respuesta = admin.get("/reporte_ventas_pdf?desde=2026-01-01")
    assert respuesta.status_code == 200
    assert respuesta.data.startswith(b"%PDF")
