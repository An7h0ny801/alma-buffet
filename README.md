# Alma Buffet

Sistema web para buffet: mostrador, caja, cocina e inventario, mesas, clientes, reservaciones, empleados, usuarios, roles y permisos, bitácoras, reportes y respaldos.

Flask 3.1 + SQLAlchemy 2.0 sobre SQL Server (local) o Azure SQL Database (producción). En producción se ejecuta en Docker con gunicorn (pensado para Render).

## Estructura

```
proyecto_produccion/
├── core/            arranque, configuración, seguridad, migraciones y comandos
├── models/          modelos SQLAlchemy (atributos snake_case → columnas camelCase)
├── routes/          blueprints (controladores HTTP)
├── services/        reglas de negocio y validaciones
├── templates/       vistas Jinja2
├── static/          CSS, JS y librerías locales (sin CDN)
├── migrations/      esquema de la base en archivos SQL numerados
├── deploy/          inicio del contenedor y configuración de gunicorn
├── tests/           pruebas automáticas (pytest) y datos de demostración
├── Dockerfile       imagen de producción (Python 3.11 + ODBC Driver 18)
├── render.yaml      blueprint de Render
├── run.py           punto de entrada (gunicorn run:app / servidor de desarrollo)
├── iniciar.bat      arranque local en Windows
└── .env.example     variables de entorno disponibles (sin valores reales)
```

## Comandos

Todos se ejecutan con `flask --app run <comando>` (en el contenedor basta `flask <comando>`).

| Comando | Qué hace |
|---|---|
| `migrar` | Aplica las migraciones pendientes de `migrations/`. `--crear-base` crea la base local si falta (no funciona en producción). |
| `inicializar-admin` | Crea el **primer** administrador. Si ya existe uno, no hace nada. `--si-falta` solo avisa cuando faltan datos. |
| `restablecer-admin --correo X` | Cambia la contraseña de un administrador. Solo en consola interactiva. |
| `crear-usuario-bd --usuario alma_app` | Crea el usuario de base de datos con permisos mínimos para la aplicación. Solo en consola interactiva. |

## Desarrollo local (Windows)

Requisitos: Python 3.10 o superior, SQL Server con *ODBC Driver 17 o 18 for SQL Server*.

1. Doble clic en `iniciar.bat`. Crea el entorno virtual, instala dependencias, crea y migra la base local `BUFFET_ALMA_PRUEBA_33` y, si no hay administrador, pide sus datos en la consola.
2. Si la instancia no es la predeterminada, copie `.env.example` a `.env` y ponga, por ejemplo, `DB_HOST=localhost\SQLEXPRESS`.

Una base creada con el script anterior (`basedatosALMABUFFET.sql`) se reconoce automáticamente: `migrar` la registra como existente y solo aplica los cambios nuevos.

Pruebas (usan una base temporal que se crea y se elimina):

```bash
pip install -r requirements-dev.txt
```

```bash
python -m pytest
```

## Producción: Azure SQL Database + Render

### 1. Base de datos en Azure

1. Cree un servidor lógico de Azure SQL y una base con la **oferta gratuita** (*Apply free offer*). En *Comportamiento al agotar el límite gratuito* elija **pausar la base hasta el mes siguiente** para no generar costos.
2. En *Configuración adicional* use la intercalación `Modern_Spanish_CI_AS`.
3. En *Redes* agregue al firewall las **IP de salida de Render** (Render → servicio → *Connect* → *Outbound*). No active "Permitir servicios de Azure" ni `0.0.0.0–255.255.255.255`.
4. Guarde el usuario administrador del servidor: se usará solo para migraciones.

### 2. Usuario con permisos mínimos (recomendado)

Desde su computadora, con el `.env` apuntando a Azure (`APP_ENV=desarrollo`, `DB_HOST=<servidor>.database.windows.net`, `DB_NAME`, `DB_MIGRACION_USER`/`DB_MIGRACION_PASSWORD` del administrador del servidor y `DB_TRUST_SERVER_CERTIFICATE=0`), agregue su IP al firewall y ejecute:

```bash
flask --app run migrar
```

```bash
flask --app run crear-usuario-bd --usuario alma_app
```

`alma_app` solo puede leer, escribir y ejecutar procedimientos; no puede alterar el esquema ni borrar la auditoría.

### 3. Servicio en Render

1. Suba **el contenido de `proyecto_produccion/`** como raíz de un repositorio privado de GitHub.
2. En Render: *New* → *Blueprint* → elija el repositorio (usa `render.yaml`, plan gratuito con Docker).
3. Complete las variables marcadas para llenar:

| Variable | Valor |
|---|---|
| `DB_HOST` | `<servidor>.database.windows.net` |
| `DB_NAME` | nombre de la base en Azure |
| `DB_USER` / `DB_PASSWORD` | `alma_app` y su contraseña |
| `DB_MIGRACION_USER` / `DB_MIGRACION_PASSWORD` | administrador del servidor (o déjelas vacías para usar `DB_USER`) |
| `ADMIN_CORREO` / `ADMIN_PASSWORD` / `ADMIN_NOMBRE` | datos del primer administrador |

`SECRET_KEY` la genera Render. Al iniciar, el contenedor aplica las migraciones, crea el primer administrador (solo si no existe ninguno) y arranca gunicorn.

4. Entre a la URL de Render con `ADMIN_CORREO`; el sistema obliga a cambiar la contraseña.
5. **Borre `ADMIN_PASSWORD`** (y, si quiere, `DB_MIGRACION_*`) de Render y vuelva a desplegar.

### Variables de entorno

| Variable | Producción | Descripción |
|---|---|---|
| `APP_ENV` | `produccion` | `desarrollo`, `produccion` o `pruebas`. |
| `SECRET_KEY` | obligatoria (≥ 32) | Firma de cookies de sesión. |
| `DB_HOST`, `DB_PORT`, `DB_NAME` | obligatorias | Servidor, puerto (1433) y base. |
| `DB_USER`, `DB_PASSWORD` | obligatorias | Credenciales de la aplicación. |
| `DB_MIGRACION_USER`, `DB_MIGRACION_PASSWORD` | opcionales | Credenciales para `migrar` y `crear-usuario-bd`. |
| `DB_ENCRYPT`, `DB_TRUST_SERVER_CERTIFICATE` | `1` / `0` | La app no arranca en producción con otros valores. |
| `DB_POOL` | `nulo` (predeterminado) | `nulo` abre una conexión por petición para que Azure pueda pausarse; `cola` usa un pool. |
| `ZONA_HORARIA_BD` | `UTC` | Zona horaria del reloj de la base (Azure usa UTC). |
| `ZONA_HORARIA` | `America/Costa_Rica` | Zona en que se muestran las fechas. |
| `SESION_DURACION_HORAS`, `SESION_INACTIVIDAD_MINUTOS` | 8 / 60 | Duración máxima e inactividad permitida. |
| `LOGIN_MAX_INTENTOS`, `LOGIN_MAX_INTENTOS_IP`, `LOGIN_VENTANA_MINUTOS` | 5 / 20 / 15 | Bloqueo temporal por intentos fallidos. |
| `PROXY_SALTOS` | 1 | Proxies de confianza delante de la app (Render = 1). |
| `ADMIN_CORREO`, `ADMIN_PASSWORD`, `ADMIN_NOMBRE` | solo el primer despliegue | Datos del primer administrador. |
| `WEB_CONCURRENCY`, `GUNICORN_THREADS`, `GUNICORN_TIMEOUT` | 2 / 4 / 120 | Ajustes de gunicorn. |

## Migraciones

Cada cambio de esquema es un archivo nuevo `NNNN_descripcion.sql` en `migrations/` (lotes separados por `GO`). `migrar` los aplica en orden, dentro de una transacción por archivo, y guarda en `TblMigraciones` su nombre y su suma SHA-256. Si un archivo aplicado se modifica, `migrar` se detiene: los cambios siempre van en un archivo nuevo.

Las migraciones siguen la convención de nombres del proyecto: tablas `Tbl`, procedimientos `pa_`, vistas `v`, funciones `fn_`, triggers `trg_`, restricciones `PK_/FK_/DF_/CK_/UQ_`, índices `idx_`, parámetros `@p` y variables `@v`.

## Respaldos

- SQL Server propio: el módulo Respaldos genera respaldos completos, diferenciales y de log en la carpeta predeterminada del servidor. Con el usuario `alma_app` el respaldo se genera, pero la casilla "Verificar" no funciona: SQL Server exige `CREATE ANY DATABASE` para `RESTORE VERIFYONLY` y ese permiso no se concede por defecto. Verifique desde SSMS o concédalo manualmente si lo necesita.
- Azure SQL Database: los respaldos son automáticos y la restauración a un punto en el tiempo se hace desde el portal. La pantalla muestra el historial y desactiva la generación manual.
