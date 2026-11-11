from tests.utilidades import CORREO_ADMIN, PASSWORD_ADMIN, crear_usuario, enviar, iniciar_sesion, texto


def prueba_login_correcto(cliente):
    respuesta = iniciar_sesion(cliente, CORREO_ADMIN, PASSWORD_ADMIN)
    assert respuesta.status_code == 302
    assert respuesta.location.endswith("/dashboard")


def prueba_login_incorrecto(cliente):
    respuesta = enviar(
        cliente, "/validar_login", {"correo": "admin@alma.com", "password": "mala"}
    )
    assert "Correo o contraseña incorrectos." in texto(respuesta)


def prueba_sin_sesion_redirige_al_login(cliente):
    respuesta = cliente.get("/dashboard")
    assert respuesta.status_code == 302
    assert "/login" in respuesta.location


def prueba_post_sin_token_csrf_es_rechazado(admin):
    respuesta = admin.post("/mesas/guardar", data={"numero_mesa": "1", "capacidad": "4"})
    assert respuesta.status_code == 400


def prueba_cerrar_sesion(admin):
    enviar(admin, "/logout")
    assert admin.get("/dashboard").status_code == 302


def prueba_cambio_de_password_obligatorio(admin, app):
    correo = crear_usuario(admin, rol="Cajero", password="Temporal1*", debe_cambiar=True)
    cliente_http = app.test_client()
    respuesta = iniciar_sesion(cliente_http, correo, "Temporal1*")
    assert "/cambiar-password" in respuesta.location
    assert "/cambiar-password" in cliente_http.get("/caja").location

    respuesta = enviar(
        cliente_http,
        "/cambiar-password",
        {
            "password_actual": "Temporal1*",
            "password_nueva": "Definitiva2*",
            "password_confirmacion": "Definitiva2*",
        },
    )
    assert "Contraseña actualizada." in texto(respuesta)
    assert cliente_http.get("/caja").status_code == 200


def prueba_permisos_por_rol(admin, app):
    correo = crear_usuario(admin, rol="Cajero", password="Cajero1*")
    cajero = app.test_client()
    iniciar_sesion(cajero, correo, "Cajero1*")
    assert cajero.get("/caja").status_code == 200
    assert cajero.get("/usuarios").status_code == 403
    assert cajero.get("/cocina").status_code == 403
