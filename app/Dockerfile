FROM python:3.10.11-slim-buster as base

# Set the environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PROJECT_PATH="/usr/src/app"
ENV VITRUAL_ENVIRONMENT_PATH="$PROJECT_PATH/.venv"
ENV PATH="$VITRUAL_ENVIRONMENT_PATH/bin:$PATH"

WORKDIR $PROJECT_PATH
EXPOSE 8000

# Create app user, app group, and the necessary directories
RUN addgroup --system app \
    && adduser --system --group app \
    && mkdir /var/log/gunicorn \
    && chown -R app:app /var/log/gunicorn \
    && mkdir "$PROJECT_PATH/storage" \
    && chown -R app:app "$PROJECT_PATH/storage"



FROM base as builder

# Install and configure poetry
ENV POETRY_VERSION=1.4.2 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
RUN pip install "poetry==$POETRY_VERSION"

# Install the production dependencies into the virtual environment
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only main \
    && rm -rf "$POETRY_CACHE_DIR"



# The dev stage has poetry installed globally,
# and have the dependencies installed in the virtual environment
FROM builder as dev

# Install the extra dependencies into the virtual environment
RUN poetry install --no-root --without main \
    && rm -rf "$POETRY_CACHE_DIR"

USER app



# The production stage does not have poetry installed,
# The production dependencies are installed in the virtual environment
FROM base as prod

# Copy the virtual environment and the code
COPY --from=builder $VITRUAL_ENVIRONMENT_PATH $VITRUAL_ENVIRONMENT_PATH
COPY . .
RUN rm -rf "$PROJECT_PATH/tests" \
    && chmod +x "$PROJECT_PATH/entrypoints/entrypoint-wsgi.sh" \
    && chmod +x "$PROJECT_PATH/entrypoints/entrypoint-asgi.sh" \
    && chmod +x "$PROJECT_PATH/entrypoints/entrypoint-dev.sh"

USER app
