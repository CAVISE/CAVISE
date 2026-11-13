# syntax=docker/dockerfile:1

ARG CARLA_VERSION=0.9.16

FROM ubuntu:20.04 AS package

ARG CARLA_VERSION

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install --no-install-recommends -y ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl --http1.1 --fail --location --retry 3 \
        "https://downloads.carlasim.com/Linux/CARLA_${CARLA_VERSION}.tar.gz" \
        --output /tmp/carla.tar.gz \
    && mkdir /package \
    && tar -xzf /tmp/carla.tar.gz -C /package \
    && test "$(cat /package/VERSION)" = "$CARLA_VERSION" \
    && rm /tmp/carla.tar.gz

FROM ubuntu:20.04 AS python

ARG PYTHON_VERSION=3.12.3

# Keep the existing Python version without shipping its compiler or pyenv.
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        build-essential ca-certificates curl libbz2-dev libffi-dev libgdbm-dev \
        liblzma-dev libncursesw5-dev libreadline-dev libsqlite3-dev libssl-dev \
        uuid-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/python

RUN curl --fail --location --retry 3 \
        "https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz" \
        --output /tmp/python.tar.gz \
    && tar -xzf /tmp/python.tar.gz --strip-components=1 \
    && ./configure --prefix=/opt/python --with-ensurepip=install \
    && make -j "$(nproc)" \
    && make install \
    && ln -s python3 /opt/python/bin/python \
    && rm /tmp/python.tar.gz

FROM ubuntu:20.04 AS default

ENV DEBIAN_FRONTEND=noninteractive

# CARLA's release runtime dependencies and the shared libraries used by Python.
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        ca-certificates fontconfig libbz2-1.0 libffi7 libgdbm6 libgdbm-compat4 liblzma5 \
        libncursesw6 libomp5 libreadline8 libsdl2-2.0-0 libsqlite3-0 libssl1.1 \
        libstdc++6 libuuid1 libvulkan1 ttf-ubuntu-font-family xdg-user-dirs xserver-xorg zlib1g \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home carla \
    && install -d -o carla -g carla /workspace

COPY --from=python /opt/python /opt/python
COPY --from=package --chown=carla:carla /package/ /workspace/

ENV PATH="/opt/python/bin:${PATH}" \
    HOME=/home/carla \
    OMP_PROC_BIND=FALSE \
    OMP_NUM_THREADS=48 \
    NVIDIA_DRIVER_CAPABILITIES=all \
    NVIDIA_VISIBLE_DEVICES=all

ARG CARLA_VERSION

COPY api/requirements.txt /tmp/carla-api-requirements.txt

RUN python -m pip install --no-cache-dir pip==26.0.1 \
    && python -m pip install --no-cache-dir \
        pygame==2.6.1 numpy==1.26.4 "carla==${CARLA_VERSION}" \
        -r /tmp/carla-api-requirements.txt \
    && python -c "import bz2, ctypes, lzma, readline, sqlite3, ssl; import carla, numpy, pygame"

WORKDIR /workspace
USER carla

CMD ["/bin/bash", "CarlaUE4.sh"]

FROM default AS extended

RUN --mount=type=bind,from=maps,source=${CARLA_VERSION},target=/workspace/Import \
    test -s "Import/AdditionalMaps_${CARLA_VERSION}.tar.gz" \
    && tar -tzf "Import/AdditionalMaps_${CARLA_VERSION}.tar.gz" > /dev/null \
    && bash ./ImportAssets.sh
