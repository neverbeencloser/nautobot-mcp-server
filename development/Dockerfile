ARG NAUTOBOT_VER
ARG PYTHON_VER

FROM ghcr.io/nautobot/nautobot-dev:${NAUTOBOT_VER}-py${PYTHON_VER}

ENV prometheus_multiproc_dir=/prom_cache

WORKDIR /source

# Configure poetry
RUN poetry config virtualenvs.create false

# Copy in only pyproject.toml/poetry.lock to help with caching this layer if no updates to dependencies
COPY pyproject.toml poetry.lock /source/

RUN poetry lock

# --no-root declares not to install the project package since we're wanting to take advantage of caching dependency installation
# and the project is copied in and installed after this step
RUN --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --no-interaction --no-ansi --no-root --with=dev

# Copy in the rest of the source code and install local Nautobot plugin
COPY . /source
COPY development/nautobot_config.py /opt/nautobot/nautobot_config.py
