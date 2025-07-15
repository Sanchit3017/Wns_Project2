#!/bin/bash
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE auth_service;
    CREATE DATABASE user_service;
    CREATE DATABASE notification_service;
    CREATE DATABASE trip_service;
EOSQL