FROM debian:bookworm-slim

ARG PYTHON_VERSION=3.10

ARG USER=sumo
ARG GROUP=sumo
ARG UID=1000
ARG GID=1000

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.9 \
    cmake=3.25.* \
    git=1:2.39.* \
    bash=5.2.* \
    ca-certificates=20230311* \
    curl=7.88.* \
    libssl-dev=3.0.* \
    libbz2-dev=1.0.* \
    zlib1g-dev=1:1.2.* \
    libxrender1=1:0.9.* \
    libsm6=2:1.2.* \
    libxext6=2:1.3.* \
    ffmpeg=7:5.1.* \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid ${GID} ${GROUP} && \
    useradd --uid ${UID} --gid ${GID} --create-home ${USER}

USER ${USER}
WORKDIR /home/${USER}

ENV PYENV_ROOT=/home/${USER}/.pyenv
ENV PATH="$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN curl https://pyenv.run | bash && \
    pyenv install ${PYTHON_VERSION} && \
    pyenv global ${PYTHON_VERSION} && \
    pyenv rehash

RUN pip install --no-cache-dir --upgrade pip==26.1.2 && \
    pip install --no-cache-dir \
    traci==1.27.0 \
    eclipse-sumo==1.27.0
