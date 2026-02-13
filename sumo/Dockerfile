FROM debian:bookworm-slim

ARG PYTHON_VERSION=3.10

ARG USER=sumo
ARG GROUP=sumo
ARG UID=1000
ARG GID=1000

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.9 \
    cmake=3.25.1-1 \
    git=1:2.39.5-0+deb12u3 \
    bash=5.2.15-2+b10 \
    ca-certificates=20230311+deb12u1 \
    curl=7.88.1-10+deb12u14 \
    libssl-dev=3.0.18-1~deb12u2 \
    libbz2-dev=1.0.8-5+b1 \
    zlib1g-dev=1:1.2.13.dfsg-1 \
    libxrender1=1:0.9.10-1.1 \
    libsm6=2:1.2.3-1 \
    libxext6=2:1.3.4-1+b1 \
    ffmpeg=7:5.1.8-0+deb12u1 \
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

RUN pip install --no-cache-dir --upgrade pip==26.0.1 && \
    pip install --no-cache-dir \
    traci==1.26.0 \
    eclipse-sumo==1.26.0
