# Install uv
FROM python:3.13-slim AS base

ENV BUILD_PACKAGES="build-essential libldap2-dev libsasl2-dev"
ENV RUNTIME_PACKAGES="libldap2 libsasl2-2"

RUN useradd -m -s /bin/bash oncall

FROM base AS build
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_LINK_MODE=copy

# Change the working directory to the `app` directory
WORKDIR /app

RUN --mount=type=cache,target=/var/lib/apt/lists <<LIBS
    set -e 
    apt-get update
    apt-get install -y --no-install-recommends $RUNTIME_PACKAGES
LIBS


# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
<<INSTALL
    set -e
    apt-get update && apt-get install --no-install-recommends -y $BUILD_PACKAGES
    uv venv
    uv sync --locked --no-install-project --no-editable --no-group dev
    apt-get purge -y $BUILD_PACKAGES
    rm -rf /var/lib/apt/lists/*
INSTALL

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv run build_assets && \
    rm -r src/oncall/ui/static/.webassets-cache/ && \
    uv sync --locked --no-editable --no-group dev

FROM base
USER oncall
COPY --from=build --chown=oncall:oncall /app/.venv /app/.venv
COPY ./db/schema.v0.sql /app/init.sql
ENTRYPOINT ["/app/.venv/bin/oncall"]
CMD ["/app/config.yaml", "--skip-build-assets"]
