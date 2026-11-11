FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    ACCEPT_EULA=Y \
    TZ=America/Costa_Rica \
    APP_ENV=produccion \
    FLASK_APP=run.py

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl gnupg tzdata \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
       | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list \
       -o /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends msodbcsql18 unixodbc \
    && apt-get purge -y --auto-remove curl gnupg \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin alma

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=root:root . .
RUN sed -i 's/\r$//' deploy/iniciar_contenedor.sh && chmod 0555 deploy/iniciar_contenedor.sh

USER alma

EXPOSE 10000

CMD ["deploy/iniciar_contenedor.sh"]
