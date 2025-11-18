ARG CARLA_VERSION=0.9.16
FROM carlasim/carla:${CARLA_VERSION}

ARG PYTHON_VERSION=3.12.3
ARG CARLA_VERSION
ARG MAPS_ARCHIVE_URL=https://carla-releases.s3.us-east-005.backblazeb2.com/Linux/AdditionalMaps_${CARLA_VERSION}.tar.gz

USER root

RUN apt-get update && apt-get install --no-install-recommends -y \
    wget \
    curl \
    git \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    fontconfig \
    ttf-ubuntu-font-family && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


USER carla
ARG CARLA_ROOT=/workspace
WORKDIR ${CARLA_ROOT}/Import

RUN wget ${MAPS_ARCHIVE_URL} && \
    cd .. && \
    ./ImportAssets.sh && \
    rm ${CARLA_ROOT}/Import/AdditionalMaps_${CARLA_VERSION}.tar.gz

WORKDIR ${CARLA_ROOT}

RUN curl https://pyenv.run | bash && \
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
RUN pip install --no-cache-dir --break-system-packages pygame numpy==1.26.4 carla==${CARLA_VERSION}
