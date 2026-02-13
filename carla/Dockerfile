ARG CARLA_VERSION=0.9.16
FROM carlasim/carla:${CARLA_VERSION}

ARG PYTHON_VERSION=3.12.3
ARG CARLA_VERSION
ARG MAPS_ARCHIVE_URL=https://carla-releases.s3.us-east-005.backblazeb2.com/Linux/AdditionalMaps_${CARLA_VERSION}.tar.gz

USER root

RUN apt-get update && apt-get install --no-install-recommends -y \
    wget=1.20.3-1ubuntu2.1 \
    curl=7.68.0-1ubuntu2.25 \
    ca-certificates=20240203~20.04.1 \
    git=1:2.25.1-1ubuntu3.14 \
    build-essential=12.8ubuntu1.1 \
    libssl-dev=1.1.1f-1ubuntu2.24 \
    zlib1g-dev=1:1.2.11.dfsg-2ubuntu1.5 \
    libbz2-dev=1.0.8-2 \
    libreadline-dev=8.0-4 \
    libsqlite3-dev=3.31.1-4ubuntu0.7 \
    libncurses5-dev=6.2-0ubuntu2.1 \
    libncursesw5-dev=6.2-0ubuntu2.1 \
    xz-utils=5.2.4-1ubuntu1.1 \
    fontconfig=2.13.1-2ubuntu3 \
    ttf-ubuntu-font-family=1:0.83-4ubuntu1 && \
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
