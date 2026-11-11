from tests.utilidades import (
    consulta,
    crear_cliente,
    crear_mesa,
    crear_usuario,
    enviar,
    nombre_unico,
    numero_unico,
    texto,
    valor,
)


def prueba_mesa_duplicada(admin):
    numero = str(numero_unico())
    enviar(admin, "/mesas/guardar", {"numero_mesa": numero, "capacidad": "4"})
    respuesta = enviar(admin, "/mesas/guardar", {"numero_mesa": numero, "capacidad": "4"})
    assert "Número de mesa repetido" in texto(respuesta)


def prueba_eliminar_mesa(admin):
    assert "Mesa eliminada." in texto(enviar(admin, f"/mesas/{crear_mesa(admin)}/eliminar"))
    assert "Mesa archivada" in texto(enviar(admin, "/mesas/2/eliminar"))
    assert valor(admin.application, "SELECT activo FROM TblMesas WHERE idMesa = 2") is False
    enviar(admin, "/mesas/guardar", {"id_mesa": "2", "numero_mesa": "2", "capacidad": "4"})


def prueba_cliente_guardar_y_eliminar(admin):
    id_cliente = crear_cliente(admin)
    respuesta = enviar(admin, f"/clientes/{id_cliente}/eliminar")
    assert "Cliente eliminado." in texto(respuesta)


def prueba_cliente_telefono_invalido(admin):
    respuesta = enviar(
        admin, "/clientes/guardar", {"nombre": nombre_unico("Ana"), "telefono": "123"}
    )
    assert "8 números" in texto(respuesta)


def prueba_empleado_con_usuario_se_archiva(admin):
    app = admin.application
    correo = crear_usuario(admin, rol="Cocinero", password="Cocina1*")
    id_empleado = valor(app, "SELECT idEmpleado FROM TblUsuarios WHERE correo = :c", c=correo)
    respuesta = enviar(admin, f"/empleados/{id_empleado}/eliminar")
    assert "archivado" in texto(respuesta)
    assert valor(app, "SELECT activo FROM TblUsuarios WHERE correo = :c", c=correo) is False


def prueba_correo_de_usuario_duplicado(admin):
    correo = crear_usuario(admin, rol="Cajero", password="Cajero1*")
    otro = crear_usuario(admin, rol="Cajero", password="Cajero1*")
    app = admin.application
    id_usuario = valor(app, "SELECT idUsuario FROM TblUsuarios WHERE correo = :c", c=otro)
    id_empleado_otro = valor(app, "SELECT idEmpleado FROM TblUsuarios WHERE idUsuario = :u", u=id_usuario)
    respuesta = enviar(
        admin,
        "/usuarios/guardar",
        {
            "id_usuario": str(id_usuario),
            "correo": correo,
            "id_rol": str(valor(app, "SELECT idRol FROM TblRoles WHERE nombre = 'Cajero'")),
            "id_empleado": str(id_empleado_otro),
            "activo": "1",
        },
    )
    assert "Ya existe un usuario con ese correo." in texto(respuesta)


def prueba_no_puede_eliminarse_a_si_mismo(admin):
    respuesta = enviar(admin, "/usuarios/1/eliminar")
    assert "No puede eliminar su propio usuario." in texto(respuesta)


def prueba_roles(admin):
    app = admin.application
    nombre = nombre_unico("Supervisor")
    respuesta = enviar(
        admin, "/roles/guardar", {"nombre": nombre, "permisos": ["caja.ver", "reportes.ver"]}
    )
    assert "Rol guardado." in texto(respuesta)
    id_rol = valor(app, "SELECT idRol FROM TblRoles WHERE nombre = :n", n=nombre)
    assert valor(app, "SELECT COUNT(*) FROM TblRolesPermisos WHERE idRol = :r", r=id_rol) == 2

    respuesta = enviar(admin, "/roles/guardar", {"nombre": nombre})
    assert "Ya existe un rol con ese nombre." in texto(respuesta)

    assert "Rol eliminado." in texto(enviar(admin, f"/roles/{id_rol}/eliminar"))
    assert "protegido" in texto(enviar(admin, "/roles/1/eliminar"))


def prueba_rol_copiando_permisos_de_otro(admin):
    app = admin.application
    nombre = nombre_unico("Copia")
    id_cocinero = valor(app, "SELECT idRol FROM TblRoles WHERE nombre = 'Cocinero'")
    enviar(admin, "/roles/guardar", {"nombre": nombre, "id_rol_base": str(id_cocinero)})
    id_rol = valor(app, "SELECT idRol FROM TblRoles WHERE nombre = :n", n=nombre)
    permisos = lambda r: {fila[0] for fila in consulta(
        app,
        "SELECT p.codigo FROM TblRolesPermisos rp JOIN TblPermisos p ON p.idPermiso = rp.idPermiso "
        "WHERE rp.idRol = :r",
        r=r,
    )}
    assert permisos(id_rol) == permisos(id_cocinero)
    enviar(admin, f"/roles/{id_rol}/eliminar")


def prueba_permisos_por_rol(admin):
    app = admin.application
    nombre = nombre_unico("Editor")
    respuesta = enviar(admin, "/roles/guardar", {"nombre": nombre, "permisos": ["caja.ver"]})
    assert "Rol guardado." in texto(respuesta)
    id_rol = valor(app, "SELECT idRol FROM TblRoles WHERE nombre = :n", n=nombre)
    codigos = lambda: {fila[0] for fila in consulta(
        app,
        "SELECT p.codigo FROM TblRolesPermisos rp JOIN TblPermisos p ON p.idPermiso = rp.idPermiso "
        "WHERE rp.idRol = :r",
        r=id_rol,
    )}

    pagina = texto(admin.get("/roles"))
    assert "Seleccione un rol" in pagina
    assert f"/roles?rol={id_rol}" in pagina
    assert "/roles?rol=1" not in pagina

    pagina = texto(admin.get(f"/roles?rol={id_rol}"))
    assert "Permisos asignados" in pagina and "Permisos que se pueden agregar" in pagina
    assert '<input type="hidden" name="permisos" value="caja.ver">' in pagina
    assert 'type="checkbox"' not in pagina
    assert "Cambios sin guardar" in pagina
    assert admin.get("/roles?rol=999999").status_code == 404
    assert "siempre tiene todos los permisos" in texto(admin.get("/roles?rol=1", follow_redirects=True))

    respuesta = enviar(admin, f"/roles/{id_rol}/permisos", {
        "permisos": ["respaldos.gestionar", "reportes.ver", "mesas.borrar"],
    })
    assert "Permisos del rol guardados." in texto(respuesta)
    assert codigos() == {"respaldos.gestionar", "respaldos.ver", "reportes.ver"}

    respuesta = enviar(admin, f"/roles/{id_rol}/permisos", {
        "permisos": ["respaldos.gestionar", "respaldos.ver", "reportes.ver"],
    })
    assert "No había cambios que guardar." in texto(respuesta)

    enviar(admin, f"/roles/{id_rol}/permisos", {})
    assert codigos() == set()

    total_admin = valor(app, "SELECT COUNT(*) FROM TblRolesPermisos WHERE idRol = 1")
    assert "siempre tiene todos los permisos" in texto(enviar(admin, "/roles/1/permisos", {}))
    assert valor(app, "SELECT COUNT(*) FROM TblRolesPermisos WHERE idRol = 1") == total_admin

    nuevo_nombre = nombre_unico("Renombrado")
    assert "Rol renombrado." in texto(enviar(admin, f"/roles/{id_rol}/renombrar", {"nombre": nuevo_nombre}))
    assert valor(app, "SELECT nombre FROM TblRoles WHERE idRol = :r", r=id_rol) == nuevo_nombre
    assert "no puede cambiar de nombre" in texto(enviar(admin, "/roles/1/renombrar", {"nombre": "Jefe"}))
    enviar(admin, f"/roles/{id_rol}/eliminar")
