# Use a full-featured Ubuntu 22.04 LTS as the base image
FROM ubuntu:22.04

# Set a label for the author
LABEL authors="alex"

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Python
RUN apt-get update && \
    apt-get install -y software-properties-common curl ca-certificates && \
    add-apt-repository ppa:deadsnakes/ppa && \
    # Add NodeSource PPA for Node.js 20.x
    apt-get update && \
    apt-get install -y python3.13 python3.13-dev python3.13-venv python3-pip python3-distutils build-essential postgresql libpq-dev nodejs && \
    # Clean up apt lists to reduce image size
    rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.13 1

WORKDIR /app

COPY . .

RUN python3 -m venv .venv && \
    .venv/bin/pip install -r Foundry-Visualization/requirements.txt

# Node
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g npm@latest && \
    npm install --prefix ./Foundry-Visualization


ENTRYPOINT ["/bin/bash", "/app/Foundry-Visualization/entrypoint.sh"]