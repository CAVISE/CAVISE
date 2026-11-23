# syntax=docker/dockerfile:1

ARG CARLA_VERSION=1.0

FROM ubuntu:24.04 AS package

ARG CARLA_VERSION

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        ca-certificates=20260816ubuntu0.24.04.* \
        curl=8.5.* \
    && rm -rf /var/lib/apt/lists/*

RUN curl --fail --location --retry 3 \
        "https://downloads.carlasim.com/Linux/CARLA_${CARLA_VERSION}.tar.gz" \
        --output /tmp/carla.tar.gz \
    && mkdir /unpack \
    && tar -xzf /tmp/carla.tar.gz -C /unpack \
    && if [ -d "/unpack/Carla-${CARLA_VERSION}-Linux-Shipping" ]; then \
        mv "/unpack/Carla-${CARLA_VERSION}-Linux-Shipping" /package; \
       else mv /unpack /package; fi \
    && test -f /package/Tools/carla_pack.py \
    && test -f /package/CarlaUnreal.sh \
    && rm /tmp/carla.tar.gz

FROM ubuntu:24.04 AS default

ENV DEBIAN_FRONTEND=noninteractive

# CARLA runtime libraries and Ubuntu's Python 3.12.
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        ca-certificates=20260816ubuntu0.24.04.* \
        fontconfig=2.15.* \
        fonts-ubuntu=0.869+* \
        libomp5=1:18.0-* \
        libsdl2-2.0-0=2.30.* \
        libvulkan1=1.3.* \
        python3=3.12.* \
        python3-venv=3.12.* \
        xdg-user-dirs=0.18-* \
        xserver-xorg=1:7.7+* \
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
        pygame==2.6.1 numpy==1.26.4 \
        /workspace/PythonAPI/carla/dist/carla-${CARLA_VERSION}-cp312-*x86_64.whl \
        -r /tmp/carla-api-requirements.txt \
    && python -c 'import carla; print(carla.Client("localhost", 2000).get_client_version())'

WORKDIR /workspace
USER 1000

FROM default AS extended

ARG CARLA_MAPS_ARCHIVE=${CARLA_VERSION}/AdditionalMaps_${CARLA_VERSION}.tar.gz

RUN --mount=type=bind,from=maps,source=${CARLA_MAPS_ARCHIVE},target=/tmp/AdditionalMaps.tar.gz \
    python Tools/carla_pack.py install /tmp/AdditionalMaps.tar.gz --server /workspace
