from datetime import date, timedelta

from tests.utilidades import (
    consulta,
    crear_cliente,
    crear_mesa,
    enviar,
    nombre_unico,
    texto,
    valor,
)


MANANA = (date.today() + timedelta(days=1)).isoformat()


def _reservar(admin, id_mesa, hora, **extra):
    datos = {
        "id_mesa": str(id_mesa),
        "cantidad_personas": "2",
        "fecha": MANANA,
        "hora_reserva": hora,
        "estado": "Confirmada",
    }
    datos.update(extra)
    return enviar(admin, "/reservaciones/guardar", datos)


def _ultima_reservacion(app):
    return valor(app, "SELECT MAX(idReservacion) FROM TblReservaciones")


def prueba_reservacion_con_cliente_existente(admin):
    respuesta = _reservar(admin, crear_mesa(admin), "19:00", id_cliente=str(crear_cliente(admin)))
    assert "Reservación guardada." in texto(respuesta)


def prueba_conflicto_de_franja(admin):
    id_mesa = crear_mesa(admin)
    id_cliente = str(crear_cliente(admin))
    _reservar(admin, id_mesa, "19:00", id_cliente=id_cliente)
    respuesta = _reservar(admin, id_mesa, "20:30", id_cliente=id_cliente)
    assert "La mesa ya tiene una reservación en esa franja." in texto(respuesta)


def prueba_capacidad_de_la_mesa(admin):
    respuesta = _reservar(
        admin,
        crear_mesa(admin, capacidad=2),
        "13:00",
        id_cliente=str(crear_cliente(admin)),
        cantidad_personas="5",
    )
    assert "supera la capacidad" in texto(respuesta)


def prueba_cliente_nuevo_cancelar_y_eliminar(admin):
    app = admin.application
    nombre = nombre_unico("Pedro")
    respuesta = _reservar(
        admin,
        crear_mesa(admin),
        "12:00",
        estado="Pendiente",
        nuevo_cliente_nombre=nombre,
        nuevo_cliente_telefono="88882222",
    )
    assert "Reservación guardada." in texto(respuesta)
    id_reservacion = _ultima_reservacion(app)

    assert "cancelada" in texto(enviar(admin, f"/reservaciones/{id_reservacion}/cancelar"))
    assert "eliminada" in texto(enviar(admin, f"/reservaciones/{id_reservacion}/eliminar"))
    assert valor(app, "SELECT COUNT(*) FROM TblClientes WHERE nombre = :n", n=nombre) == 0

    acciones = [
        fila[0]
        for fila in consulta(
            app,
            "SELECT accion FROM TblHistorialReservaciones WHERE idReservacion = :r "
            "ORDER BY idHistorialReservacion",
            r=id_reservacion,
        )
    ]
    assert acciones == ["INSERT", "UPDATE", "DELETE"]
