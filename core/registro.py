import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


FORMATO = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def configurar_registro(app):
    raiz = logging.getLogger()
    raiz.setLevel(logging.DEBUG if app.debug else logging.INFO)
    if not any(getattr(manejador, "_alma_consola", False) for manejador in raiz.handlers):
        consola = logging.StreamHandler(sys.stdout)
        consola.setFormatter(logging.Formatter(FORMATO))
        consola._alma_consola = True
        raiz.addHandler(consola)
    logging.getLogger("werkzeug").setLevel(logging.INFO)

    carpeta = app.config.get("CARPETA_REGISTROS")
    if not carpeta or app.testing:
        return
    Path(carpeta).mkdir(parents=True, exist_ok=True)
    archivo = str(Path(carpeta) / "alma_buffet.log")
    if any(getattr(manejador, "baseFilename", None) == archivo for manejador in raiz.handlers):
        return
    manejador_archivo = RotatingFileHandler(
        archivo, maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    manejador_archivo.setLevel(logging.WARNING)
    manejador_archivo.setFormatter(logging.Formatter(FORMATO))
    raiz.addHandler(manejador_archivo)
