FROM debian:bookworm-slim

ARG PYTHON_VERSION=3.10
ARG SUMO_VERSION=v1_22_0

# :)
ARG USER=sumo
ARG GROUP=sumo
ARG UID=1000
ARG GID=1000

RUN apt update && apt install -y \
    build-essential \
    cmake \
    git \
    bash \
    curl \
    libssl-dev \
    libbz2-dev \
    zlib1g-dev \
    libxrender1 \
    libsm6 \
    libxext6 \
    ffmpeg

RUN groupadd --gid ${GID} ${GROUP} && \
    useradd --uid ${UID} --gid ${GID} --create-home ${USER}

USER ${USER}
WORKDIR /home/${USER}

ENV PYENV_ROOT=/home/${USER}/.pyenv
ENV PATH="$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH"

RUN curl https://pyenv.run | bash && \
    pyenv install ${PYTHON_VERSION} && \
    pyenv global ${PYTHON_VERSION} && \
    pyenv rehash


RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    traci eclipse-sumo

  