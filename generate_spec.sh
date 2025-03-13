#!/bin/bash

set -e
custom_path=$1
# Generate openapi file
poetry config virtualenvs.create true
poetry config http-basic.jfrog "${JFROG_USERNAME}" "${JFROG_PASSWORD}"
if [ -z "${custom_path}" ]; then
    poetry run python main.py  --openapi-file healthz_swagger.json 
else
    poetry run python main.py  --openapi-file "${custom_path}/healthz_swagger.json"
fi
