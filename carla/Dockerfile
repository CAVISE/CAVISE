ARG CARLA_VERSION=0.9.15
FROM carlasim/carla:${CARLA_VERSION}

ARG PYTHON_VERSION=3.10.11
ARG CARLA_VERSION
ARG MAPS_ARCHIVE_URL=https://carla-releases.s3.us-east-005.backblazeb2.com/Linux/AdditionalMaps_${CARLA_VERSION}.tar.gz

USER root
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    gcc \
    make \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    fontconfig \
    ttf-ubuntu-font-family


USER carla
WORKDIR /home/carla/Import
RUN wget ${MAPS_ARCHIVE_URL}

WORKDIR /home/carla
RUN ./ImportAssets.sh

RUN curl https://pyenv.run | bash

ENV HOME=/home/carla
ENV PYENV_ROOT=${HOME}/.pyenv
ENV PATH=${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}

RUN pyenv install ${PYTHON_VERSION} && \
    pyenv global ${PYTHON_VERSION} && \
    pyenv rehash

RUN pip install --break-system-packages pygame numpy==1.26.4 carla==${CARLA_VERSION}