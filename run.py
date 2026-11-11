import os

from core.aplicacion import crear_app
from core.configuracion import es_produccion, variable_booleana, variable_entera


app = crear_app()


def iniciar_desarrollo():
    if es_produccion():
        raise SystemExit(
            "El servidor de desarrollo no se usa en producción. Inicie con: "
            "gunicorn -c deploy/gunicorn.conf.py run:app"
        )
    app.run(
        host=os.getenv("APP_HOST", "127.0.0.1"),
        port=variable_entera("APP_PORT", 5000),
        debug=variable_booleana("FLASK_DEBUG"),
    )


if __name__ == "__main__":
    iniciar_desarrollo()
