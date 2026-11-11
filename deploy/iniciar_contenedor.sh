#!/bin/sh
set -eu

flask migrar
flask inicializar-admin --si-falta

exec gunicorn --config deploy/gunicorn.conf.py run:app
