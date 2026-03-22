# Use a full-featured Ubuntu 22.04 LTS as the base image
FROM ubuntu:22.04

# Set a label for the author
LABEL authors="alex"

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary dependencies, add the PPA for Python, and install Python 3.13
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.13 python3.13-dev python3.13-venv python3-pip python3-distutils build-essential postgresql libpq-dev && \
    # Clean up apt lists to reduce image size
    rm -rf /var/lib/apt/lists/*


RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.13 1

# Set the working directory
WORKDIR /app

COPY . .

RUN python3 -m venv .venv && \
    .venv/bin/pip install -r Foundry-Orchestration/requirements.txt

# Create directory for local DuckDB files
RUN mkdir -p /app/db

# PostgreSQL 18 for SQLMesh state management
# based on https://www.postgresql.org/download/linux/ubuntu/
RUN apt update && apt install -y postgresql-common && \
    apt install -y curl ca-certificates && \
    curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc && \
    install -d /usr/share/postgresql-common/pgdg && \
    . /etc/os-release && \
    sh -c "echo 'deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt $VERSION_CODENAME-pgdg main' > /etc/apt/sources.list.d/pgdg.list" && \
    apt update && \
    apt install -y postgresql-18 && \
    mkdir /postgres_data && \
    chown postgres:postgres /postgres_data

ENTRYPOINT ["/bin/bash", "/app/Foundry-Orchestration/entrypoint.sh"]

