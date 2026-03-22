#!/bin/bash
set -o errexit   # abort on nonzero exitstatus
set -o nounset   # abort on unbound variable
set -o pipefail  # don't hide errors within pipes

# Ensure the DuckDB directory exists
mkdir -p /app/db

POSTGRES_DATA_DIR="/postgres_data"
POSTGRES_LOG="${POSTGRES_DATA_DIR}/log"

# Ensure the postgres directory exists and the postgres user owns it
# before dropping privileges, otherwise pg_ctl init will fail.
mkdir -p "${POSTGRES_DATA_DIR}"
chown -R postgres:postgres "${POSTGRES_DATA_DIR}"

# checking if the postgresql has already initialized the database;
# if not, we'll init now
DB_EXISTS_FILE="${POSTGRES_DATA_DIR}/PG_VERSION"
# Check if the file exists
if [ -f "$DB_EXISTS_FILE" ]; then
    echo "File $DB_EXISTS_FILE exists. Assuming the ${POSTGRES_DATA_DIR} contains PostgreSQL database files."
    echo "Starting PostgreSQL"
    su -s /bin/bash postgres -c "/usr/lib/postgresql/18/bin/pg_ctl -D \"${POSTGRES_DATA_DIR}\" -l \"${POSTGRES_LOG}\" start -w"

else
    echo "File $DB_EXISTS_FILE not found. Initializing PostgreSQL at ${POSTGRES_DATA_DIR}"
    su -s /bin/bash postgres -c "/usr/lib/postgresql/18/bin/pg_ctl init -D \"${POSTGRES_DATA_DIR}\""

    echo "Starting PostgreSQL"
    su -s /bin/bash postgres -c "/usr/lib/postgresql/18/bin/pg_ctl -D \"${POSTGRES_DATA_DIR}\" -l \"${POSTGRES_LOG}\" start -w"

    echo "Creating database and user for sql mesh"
    # The heredoc runs in the root shell context, so environment variables
    # are expanded cleanly before being passed through to psql.
    su -s /bin/bash postgres -c "psql" <<EOF
CREATE USER "${SQLMESH_POSTGRES_USER}" WITH PASSWORD '${SQLMESH_POSTGRES_PASSWORD}';
CREATE DATABASE "${SQLMESH_POSTGRES_DATABASE}" OWNER "${SQLMESH_POSTGRES_USER}";
GRANT ALL PRIVILEGES ON DATABASE "${SQLMESH_POSTGRES_DATABASE}" TO "${SQLMESH_POSTGRES_USER}";
EOF
fi

# for the sqlmesh bin
export PATH="/app/.venv/bin:${PATH}"
/app/.venv/bin/python /app/Foundry-Orchestration/City-Main.py