# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.13.1
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr.
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

# Create a non-privileged user.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Install dependencies.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Create and set ownership of the static directory.
RUN mkdir -p /usr/src/app/static && chown -R appuser:appuser /usr/src/app/static

# Copy the source code into the container.
COPY --chown=appuser:appuser . .

# Switch to the non-privileged user.
USER appuser

EXPOSE 8000

ENTRYPOINT [ "./docker-entrypoint.sh" ]