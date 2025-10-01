#!/bin/sh

set -eu

uvicorn --host 0.0.0.0 --port 8000 "--proxy-headers" "--forwarded-allow-ips" "*" backend.main:create_app --factory
