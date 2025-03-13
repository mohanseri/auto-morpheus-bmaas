#!/bin/bash -xe

# Script used when bootstrapping the dev-env container before running contract framework
# for the current repo. Generally called after start-dev-env.sh

# make sure this path matches jenkins job clone path
pushd ${REPO_PATH}

# setup jfrog and poetry venv
export PATH=$PATH:/usr/local/lib/pact/bin
poetry config virtualenvs.create true
poetry config http-basic.jfrog ${JFROG_USERNAME} ${JFROG_PASSWORD}
poetry install
STATUS=$?

popd
# exit with the status of the poetry install
exit ${STATUS}