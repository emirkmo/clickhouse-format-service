# https://github.com/thehale/docker-python-poetry
# FROM thehale/python-poetry:1.6.1-py3.12-slim
FROM python:3.12-slim-bookworm as poetry-installer

ARG POETRY_VERSION=1.7.1

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VERSION=${POETRY_VERSION} \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && apt-get install --no-install-recommends -y build-essential \
    && rm -rf /var/lib/apt/lists/* && apt-get purge -y --auto-remove \
    && rm -rf /etc/apt/sources.list.d/temp.list

# https://python-poetry.org/docs/#installing-manually
RUN python -m venv ${POETRY_HOME}
RUN ${POETRY_HOME}/bin/pip install -U pip setuptools
RUN ${POETRY_HOME}/bin/pip install "poetry==${POETRY_VERSION}"

FROM poetry-installer as dependency-installer

ENV PYTHONUNBUFFERED=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
COPY poetry.lock /app/poetry.lock
RUN touch README.md

RUN ${POETRY_HOME}/bin/poetry install --no-root --without=dev && rm -rf $POETRY_CACHE_DIR

FROM python:3.12-slim-bookworm as production-image

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"
COPY --from=dependency-installer ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=dependency-installer /app/pyproject.toml /app/pyproject.toml

# Copy the application's source code to the /app directory
COPY clickhouse_format_service ./clickhouse_format_service

EXPOSE 8080

CMD ["uvicorn", "clickhouse_format_service.api:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers", "--log-level", "info"]
