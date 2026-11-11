from tests.utilidades import (
    crear_mesa,
    crear_producto,
    crear_ticket,
    enviar,
    texto,
    valor,
)


def _stock(app, id_producto):
    return valor(app, "SELECT stockUnidades FROM TblProductos WHERE idProducto = :p", p=id_producto)


def _estado(app, id_ticket):
    return valor(app, "SELECT estado FROM TblTickets WHERE idTicket = :t", t=id_ticket)


def prueba_crear_ticket_descuenta_inventario(admin):
    app = admin.application
    id_producto = crear_producto(admin, stock=10)
    respuesta = enviar(admin, "/tickets/enviar", {f"cantidad_{id_producto}": "3"})
    assert "enviado a caja" in texto(respuesta)
    assert _stock(app, id_producto) == 7


def prueba_ticket_vacio_rechazado(admin):
    respuesta = enviar(admin, "/tickets/enviar", {})
    assert "Debe seleccionar al menos un producto." in texto(respuesta)


def prueba_stock_insuficiente(admin):
    id_producto = crear_producto(admin, stock=2)
    respuesta = enviar(admin, "/tickets/enviar", {f"cantidad_{id_producto}": "5"})
    assert "No hay stock suficiente" in texto(respuesta)


def prueba_un_solo_fresco_gratuito(admin):
    respuesta = enviar(admin, "/tickets/enviar", {"cantidad_48": "2"})
    assert "Solo se permite un vaso de fresco gratuito por ticket." in texto(respuesta)


def prueba_tarjeta_rechazada_deja_ticket_pendiente(admin):
    app = admin.application
    id_ticket = crear_ticket(admin, {crear_producto(admin): 1})
    respuesta = enviar(
        admin,
        f"/caja/ticket/{id_ticket}/pagar",
        {"metodo_pago": "Tarjeta", "modalidad": "llevar", "resultado_tarjeta": "rechazado"},
    )
    assert "rechazó la transacción" in texto(respuesta)
    assert _estado(app, id_ticket) == "Pendiente"


def prueba_pago_en_mesa_y_liberacion(admin):
    app = admin.application
    id_producto = crear_producto(admin, precio="2500")
    id_mesa = crear_mesa(admin)
    id_ticket = crear_ticket(admin, {id_producto: 2})

    respuesta = enviar(
        admin,
        f"/caja/ticket/{id_ticket}/pagar",
        {"metodo_pago": "Tarjeta", "modalidad": "local", "id_mesa": str(id_mesa)},
    )
    assert respuesta.status_code == 200
    assert _estado(app, id_ticket) == "Pagado"

    monto = valor(app, "SELECT montoTotal FROM TblPagos WHERE idTicket = :t", t=id_ticket)
    total_vista = valor(app, "SELECT total FROM vCaja WHERE idTicket = :t", t=id_ticket)
    assert monto == total_vista == 5650
    referencia = valor(app, "SELECT referencia FROM TblPagos WHERE idTicket = :t", t=id_ticket)
    assert referencia.startswith("DATA-")

    otro_ticket = crear_ticket(admin, {id_producto: 1})
    respuesta = enviar(
        admin,
        f"/caja/ticket/{otro_ticket}/pagar",
        {"metodo_pago": "Efectivo", "modalidad": "local", "id_mesa": str(id_mesa)},
    )
    assert "ya no está disponible" in texto(respuesta)

    respuesta = enviar(admin, f"/mesas/{id_mesa}/liberar")
    assert "liberada" in texto(respuesta)
    assert valor(
        app, "SELECT fechaHoraFin FROM TblTickets WHERE idTicket = :t", t=id_ticket
    ) is not None


def prueba_pago_para_llevar_con_sinpe(admin):
    app = admin.application
    id_ticket = crear_ticket(admin, {crear_producto(admin): 1})
    enviar(
        admin,
        f"/caja/ticket/{id_ticket}/pagar",
        {"metodo_pago": "SINPE", "modalidad": "llevar", "referencia": "123456"},
    )
    assert _estado(app, id_ticket) == "Pagado"
    assert valor(app, "SELECT referencia FROM TblPagos WHERE idTicket = :t", t=id_ticket) == "123456"
    assert valor(app, "SELECT idMesa FROM TblTickets WHERE idTicket = :t", t=id_ticket) is None


def prueba_anular_devuelve_inventario(admin):
    app = admin.application
    id_producto = crear_producto(admin, stock=10)
    id_ticket = crear_ticket(admin, {id_producto: 4})
    assert _stock(app, id_producto) == 6
    respuesta = enviar(admin, f"/tickets/{id_ticket}/anular")
    assert "anulado" in texto(respuesta)
    assert _estado(app, id_ticket) == "Anulado"
    assert _stock(app, id_producto) == 10


def prueba_factura_y_pdf(admin):
    id_ticket = crear_ticket(admin, {crear_producto(admin): 1})
    enviar(admin, f"/caja/ticket/{id_ticket}/pagar", {"metodo_pago": "Efectivo", "modalidad": "llevar"})
    assert admin.get(f"/factura/{id_ticket}").status_code == 200
    pdf = admin.get(f"/factura_pdf/{id_ticket}")
    assert pdf.status_code == 200
    assert pdf.data.startswith(b"%PDF")


def prueba_bitacora_de_detalles(admin):
    id_ticket = crear_ticket(admin, {crear_producto(admin): 2})
    acciones = valor(
        admin.application,
        "SELECT COUNT(*) FROM TblHistorialDetalleTicket WHERE idTicket = :t AND accion = 'INSERT'",
        t=id_ticket,
    )
    assert acciones == 1
