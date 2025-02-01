ARG CARLA_VERSION=0.9.15
FROM carlasim/carla:${CARLA_VERSION}

ARG PYTHON_VERSION=3.10.11
ARG CARLA_VERSION
ARG MAPS_ARCHIVE_URL=https://carla-releases.s3.us-east-005.backblazeb2.com/Linux/AdditionalMaps_${CARLA_VERSION}.tar.gz

USER root

# Fix 403 error
RUN rm -f /etc/apt/sources.list.d/cuda.list && \
    rm -f /etc/apt/sources.list.d/nvidia-ml.list && \
    apt-key del 7fa2af80 && \
    apt-key del 3bf863cc

RUN apt-get update && apt-get install --no-install-recommends -y \
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
    ttf-ubuntu-font-family && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


USER carla
WORKDIR /home/carla/Import

RUN wget ${MAPS_ARCHIVE_URL} && \
    cd .. && \
    ./ImportAssets.sh && \
    rm /home/carla/Import/AdditionalMaps_${CARLA_VERSION}.tar.gz

WORKDIR /home/carla

RUN curl https://pyenv.run | bash && \
    rm -rf /tmp/*

ENV HOME=/home/carla
ENV PYENV_ROOT=${HOME}/.pyenv
ENV PATH=${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}

RUN pyenv install ${PYTHON_VERSION} && \
    pyenv global ${PYTHON_VERSION} && \
    pyenv rehash && \
    rm -rf ${PYENV_ROOT}/sources/*

RUN pip install --no-cache-dir --break-system-packages pygame numpy==1.26.4 carla==${CARLA_VERSION}