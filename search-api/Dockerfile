# Multi-stage Dockerfile for search-api (same pattern as bcros-common doc-api / notify-api, person-search bor-api)
#   - runtime   (DEFAULT, last stage): distroless image for the API service
#   - migration: full Python environment for the db migration job (/code/update_db.sh)
#
# `runtime` MUST remain the LAST stage so that `docker build` without `--target`
# produces the API image. The Cloud Build SRE helper builds the main image without
# `--target`, then builds `--target migration` for the parallel search-api-migration image.
#
#   docker build -t search-api .
#   docker build --target migration -t search-api-migration .

FROM python:3.13-slim-trixie AS builder

USER root

ARG VCS_REF="missing"
ARG BUILD_DATE="missing"

ENV VCS_REF=${VCS_REF}
ENV BUILD_DATE=${BUILD_DATE}

LABEL org.label-schema.vcs-ref=${VCS_REF} \
    org.label-schema.build-date=${BUILD_DATE}

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # pip:
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_DEFAULT_TIMEOUT=100 \
  PIP_ROOT_USER_ACTION=ignore \
  # poetry (install into /code/.venv so it can be copied into the later stages):
  POETRY_VERSION=2.1.1 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=true \
  POETRY_VIRTUALENVS_IN_PROJECT=true \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  POETRY_INSTALLER_PARALLEL=false

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

# git is needed for the sbc-connect-common git dependencies.
RUN apt-get update && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
    build-essential \
    ca-certificates \
    curl \
    git \
  && curl -sSL 'https://install.python-poetry.org' | python - \
  && poetry --version \
  # Cleaning cache:
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Copy only requirements, to cache them in docker layer
COPY ./poetry.lock ./pyproject.toml ./README.md /code/
COPY ./src /code/src

RUN --mount=type=cache,target="$POETRY_CACHE_DIR" \
  poetry install --only main --no-interaction --no-ansi

COPY . /code

# cache/ (FileSystemCache) must be writable at runtime.
# Chown to UID/GID 65532, the 'nonroot' user baked into the distroless runtime image.
RUN mkdir -p /code/cache \
  && chmod +x /code/update_db.sh \
  && chown -R 65532:65532 /code

# ---------------------------------------------------------------------------
# TARGET: migration
# Used by the search-api-db-migration-<env> Cloud Run job, which runs /code/update_db.sh.
# Placed BEFORE `runtime` so that the default build produces the runtime image.
# ---------------------------------------------------------------------------
FROM python:3.13-slim-trixie AS migration

ARG VCS_REF="missing"
ARG BUILD_DATE="missing"

LABEL org.label-schema.vcs-ref=${VCS_REF} \
    org.label-schema.build-date=${BUILD_DATE}

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  PATH="/code/.venv/bin:$PATH"

WORKDIR /code

COPY --from=builder /code /code

USER 65532:65532

CMD ["/code/update_db.sh"]

# ---------------------------------------------------------------------------
# TARGET: runtime  (DEFAULT, last stage)
# Distroless: no shell, no package manager, no pip. Runs as 'nonroot' (65532).
# gunicorn_config.py still reads GUNICORN_PROCESSES/THREADS/TIMEOUT from the env,
# and gunicorn binds to 0.0.0.0:$PORT when no --bind is given.
# ---------------------------------------------------------------------------
FROM gcr.io/distroless/python3-debian13:nonroot AS runtime

ARG VCS_REF="missing"
ARG BUILD_DATE="missing"

LABEL org.label-schema.vcs-ref=${VCS_REF} \
    org.label-schema.build-date=${BUILD_DATE}

ENV PORT=8080 \
  # Make the venv importable without its bin/python symlink
  # (distroless python lives at /usr/bin/python, not /usr/local/bin).
  PYTHONPATH="/code/src:/code/.venv/lib/python3.13/site-packages" \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1

WORKDIR /code

COPY --from=builder /code /code

USER 65532:65532

ENTRYPOINT ["python", "-m", "gunicorn", "--config", "/code/gunicorn_config.py", "wsgi:application"]
