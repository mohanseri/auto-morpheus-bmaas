#!/bin/bash -x

# Script used by the Jenkins jobs that run Lint checks, UTs, CTs, etc.
# when the job needs to run commands within the ccs-dev container of dev-env. I.e. this
# script runs in the context of the Jenkins job work directory.

# docker compose project name passed by the jenkins job
DC_PROJECT_NAME=$1

# path to script relative to the account-management/ dir that needs to be run in the ccs-dev container
COMMAND=$2

# the command arguments to be passed to the script
# FIXME look for a less hardcoded way to fetch the remaining arguments
COMMAND_ARGS=${@:3}

# Directory where the application repository is re-cloned. Verify this path matches the
# path used to clone the repo within the Jenkinsfile_CI
REPO_PATH=/home/dev/repo/ws/${APP_NAME}

# Argument parser
display_usage() {
    echo "Script to run any given script in the ccs-dev dev-env container"
    echo "Usage: `basename "$0"` <docker-compose project name> <script path relative to repo> \n"
    echo "<script path relative to repo> should be relative to ${REPO_PATH}"
}

# verify a valid script file and docker compose project name was passed
if [  $# -lt 2 ]; then
    display_usage
    exit 1
fi

echo "Docker compose project name: ${DC_PROJECT_NAME}"
echo "Script to execute in ccs-dev: ${COMMAND} in directory ${REPO_PATH}"

# if the docker-compose file doesn't exist. make sure that is made clear
DC_FILE_NAME=docker-compose_linux.yml
[ ! -f ${DC_FILE_NAME} ] \
    && echo "The docker-compose file ${DC_FILE_NAME} does not exist. Make sure the directory context is correct." \
    && exit 1


echo "Running command/script in ccs-dev with host environment variables:"
env

# Run the given script in the ccs-dev container with the remaining command arguments
# TODO run as non-root user. poetry install fails for non-root users for now.
# NOTE:
#   - Pact and target branch env vars are used for CTs.
#   - Any env var value not provided remains empty. No need to remove the -e flag.
docker-compose \
    --project-name ${DC_PROJECT_NAME} \
    --file ${DC_FILE_NAME} \
    run \
    -T \
    -e REPO_PATH=${REPO_PATH} \
    -e APP_NAME=${APP_NAME} \
    -e targetBranch=${targetBranch} \
    -e JFROG_USERNAME=${jfrog_user} \
    -e JFROG_PASSWORD=${jfrog_passwd} \
    -e PACT_USER=${pact_user} \
    -e PACT_PWD=${pact_pwd} \
    -e PR_USER=${pr_user} \
    -e PR_PWD=${pr_pwd} \
    -e JENKINS_HOME=${JENKINS_HOME} \
    -e JENKINS_USER=${jenkins_user} \
    -e JENKINS_PWD=${jenkins_pwd} \
    --workdir=${REPO_PATH} \
    ccs-dev \
    ${COMMAND} ${COMMAND_ARGS}