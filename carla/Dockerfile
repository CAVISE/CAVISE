ARG CARLA_VERSION=0.9.16
FROM carlasim/carla:${CARLA_VERSION}

ARG PYTHON_VERSION=3.12.3
ARG CARLA_VERSION
ARG MAPS_ARCHIVE_URL=https://carla-releases.s3.us-east-005.backblazeb2.com/Linux/AdditionalMaps_${CARLA_VERSION}.tar.gz

USER root

# Версии взяты для базового образа Ubuntu 22.04 (jammy), на котором основан carlasim/carla:0.9.16
RUN apt-get update && apt-get install --no-install-recommends -y \
    wget=1.21.2-2ubuntu1 \
    git=1:2.34.1-1ubuntu9 \
    build-essential=12.8ubuntu1 \
    libssl-dev=3.0.2-0ubuntu1 \
    zlib1g-dev=1:1.2.11.dfsg-2ubuntu9 \
    libbz2-dev=1.0.8-5build1 \
    libreadline-dev=8.1.2-1ubuntu3 \
    libsqlite3-dev=3.37.2-2ubuntu0.1 \
    libncurses5-dev=6.3-2ubuntu0.1 \
    libncursesw5-dev=6.3-2ubuntu0.1 \
    xz-utils=5.2.5-2ubuntu1 \
    fontconfig=2.13.1-4.2ubuntu5 \
    ttf-ubuntu-font-family=1:0.83-6ubuntu1 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


USER carla
ARG CARLA_ROOT=/workspace
WORKDIR ${CARLA_ROOT}/Import

RUN wget --progress=dot:giga ${MAPS_ARCHIVE_URL} && \
    ${CARLA_ROOT}/ImportAssets.sh && \
    rm ${CARLA_ROOT}/Import/AdditionalMaps_${CARLA_VERSION}.tar.gz

WORKDIR ${CARLA_ROOT}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN wget -qO- https://pyenv.run | bash && \
    rm -rf /tmp/*

ENV HOME=/home/carla
ENV PYENV_ROOT=${HOME}/.pyenv
ENV PATH=${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}

RUN pyenv install ${PYTHON_VERSION} && \
    pyenv global ${PYTHON_VERSION} && \
    pyenv rehash && \
    rm -rf ${PYENV_ROOT}/sources/*

USER root
RUN apt-get purge -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev libncurses5-dev libncursesw5-dev xz-utils && \
    apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

USER carla
RUN pip install --no-cache-dir --break-system-packages \
    pygame==2.5.2 \
    numpy==1.26.4 \
    carla==${CARLA_VERSION}
