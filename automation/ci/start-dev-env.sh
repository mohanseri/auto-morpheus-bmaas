#!/bin/bash -xe

# Script used by the Jenkins jobs that run Lint checks, UTs, CTs, etc
# to start the dev-env.

# docker compose project name passed by the jenkins job
DC_PROJECT_NAME=$1

# The services that will be brought up. Defaults to services needed by the CI
SERVICES=${2:-"ccs-dev ccs-redis ccs-pg"}

# Argument parser
display_usage() {
    echo "Script to start the ${SERVICES} container"
    echo "Usage: `basename "$0"` <docker-compose project name>"
}

if [  $# -lt 1 ]; then
    display_usage
    exit 1
fi

echo "Starting dev-env with docker-compose project name ${DC_PROJECT_NAME} in directory ${PWD}"

# bring up the container(s) in dev-env with a custom project name
# NOTE: assumes the OS is linux & project name is set in CI file
docker-compose \
    --project-name ${DC_PROJECT_NAME} \
    --file docker-compose_linux.yml \
    up \
    --detach \
    --build \
    ${SERVICES}

# TODO run the dev-env/tools/ci/validate.sh to make sure the services are running