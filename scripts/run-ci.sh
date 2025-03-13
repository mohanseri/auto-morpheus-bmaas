#/bin/bash

set -e
set -x

[ -f ${APP_ROOT_DIR}/.venv/bin/activate ] && . ${APP_ROOT_DIR}/.venv/bin/activate

# lint check
poetry run scripts/lint.sh

# Run UT
# poetry run test