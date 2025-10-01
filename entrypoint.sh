#!/bin/sh

set -eu

if [ "${LOAD_RUSSIA_REGIONS:-true}" = "true" ]; then
    echo "Starting Russia regions data loading in background..."
    python scripts/load_russia_regions.py &
    LOAD_PID=$!
    echo "Data loading process started with PID: $LOAD_PID"
fi


uvicorn --host 0.0.0.0 --port 8000 "--proxy-headers" "--forwarded-allow-ips" "*" backend.main:create_app --factory
