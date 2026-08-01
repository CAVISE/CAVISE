# hadolint global ignore=DL3066
ARG CARLA_VERSION=0.9.16
FROM carlasim/carla:${CARLA_VERSION}

ARG PYTHON_VERSION=3.12.3
ARG CARLA_VERSION
ARG MAPS_ARCHIVE_URL=https://carla-releases.s3.us-east-005.backblazeb2.com/Linux/AdditionalMaps_${CARLA_VERSION}.tar.gz

USER root

RUN apt-get update && apt-get install --no-install-recommends -y \
    wget=1.20.* \
    curl=7.68.* \
    ca-certificates=20240203~20.04.* \
    git=1:2.25.* \
    build-essential=12.8* \
    libssl-dev=1.1.* \
    zlib1g-dev=1:1.2.* \
    libbz2-dev=1.0.* \
    libreadline-dev=8.0-* \
    libsqlite3-dev=3.31.* \
    libncurses5-dev=6.2-* \
    libncursesw5-dev=6.2-* \
    xz-utils=5.2.* \
    fontconfig=2.13.* \
    ttf-ubuntu-font-family=1:0.83-* && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


USER carla
ARG CARLA_ROOT=/workspace
WORKDIR ${CARLA_ROOT}

RUN wget --progress=dot:giga ${MAPS_ARCHIVE_URL} -P ${CARLA_ROOT}/Import && \
    ${CARLA_ROOT}/ImportAssets.sh && \
    rm ${CARLA_ROOT}/Import/AdditionalMaps_${CARLA_VERSION}.tar.gz

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
RUN pip install --no-cache-dir --upgrade pip==26.0.1 && \
    pip install --no-cache-dir --break-system-packages \
    pygame==2.6.1 \
    numpy==1.26.4 \
    carla==${CARLA_VERSION}
