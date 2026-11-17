# syntax=docker/dockerfile:1

ARG CARLA_VERSION=0.9.16

FROM ubuntu:24.04 AS package

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

FROM ubuntu:24.04 AS default

ENV DEBIAN_FRONTEND=noninteractive

# CARLA runtime libraries and Ubuntu's Python 3.12.
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        ca-certificates fontconfig fonts-ubuntu libomp5 libsdl2-2.0-0 \
        libvulkan1 python3 python3-venv xdg-user-dirs xserver-xorg \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m venv /opt/venv

# Ubuntu's base image may already assign UID 1000 to its default user.
RUN if id ubuntu > /dev/null 2>&1; then userdel -r ubuntu; fi \
    && ! getent passwd 1000 \
    && groupadd --gid 1000 carla \
    && useradd --create-home --uid 1000 --gid 1000 carla \
    && install -d -o carla -g carla /workspace

COPY --from=package --chown=carla:carla /package/ /workspace/

ENV PATH="/opt/venv/bin:${PATH}" \
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
USER 1000

CMD ["/bin/bash", "CarlaUE4.sh"]

FROM default AS extended

ARG CARLA_MAPS_ARCHIVE=${CARLA_VERSION}/AdditionalMaps_${CARLA_VERSION}.tar.gz

RUN --mount=type=bind,from=maps,source=${CARLA_MAPS_ARCHIVE},target=/workspace/Import/AdditionalMaps.tar.gz \
    test -s Import/AdditionalMaps.tar.gz \
    && bash ./ImportAssets.sh
