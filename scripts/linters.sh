#!/bin/bash -ex

LIBS_DIR="hpe_morpheus_automation_libs"


if [ -z "${MYPY_DISABLED}" ]; then
  if [ -z ${MYPY_SRC_DIRS+x} ]; then
    MYPY_SRC_DIRS=$LIBS_DIR
  fi
  echo "Running mypy checks for source code in ${MYPY_SRC_DIRS} with directory context $(pwd)"

  eval "arr=($MYPY_SRC_DIRS)"
  for src_dir in "${arr[@]}"; do
      [ ! -d ./${src_dir} ] \
          && echo "Directory ${src_dir} not present" \
          && exit 1
  done

  if [ -z ${MYPY_ARGS+x} ]; then
    MYPY_ARGS="--ignore-missing-imports --module"
  fi

  mypy ${MYPY_ARGS} ${MYPY_SRC_DIRS}
  echo "Done with mypy"
fi

# black code
if [ -z "${BLACK_DISABLED}" ]; then
  if [ -z ${BLACK_SRC_DIRS+x} ]; then
    BLACK_SRC_DIRS=$LIBS_DIR
  fi
  echo "Running black checks for source code in ${BLACK_SRC_DIRS} with directory context $(pwd)"

  eval "arr=($BLACK_SRC_DIRS)"
  for src_dir in "${arr[@]}"; do
      [ ! -d ./${src_dir} ] \
          && echo "Directory ${src_dir} not present" \
          && exit 1
  done

  if [ -z ${BLACK_ARGS+x} ]; then
    BLACK_ARGS="--check --diff --line-length 120"
  fi

  black ${BLACK_ARGS} ${BLACK_SRC_DIRS}
  echo "Done with black"
fi

# isort code
if [ -z "${ISORT_DISABLED}" ]; then
  if [ -z ${ISORT_SRC_DIRS+x} ]; then
    ISORT_SRC_DIRS=$LIBS_DIR
  fi
  echo "Running isort checks for source code in ${ISORT_SRC_DIRS} with directory context $(pwd)"

  eval "arr=($ISORT_SRC_DIRS)"
  for src_dir in "${arr[@]}"; do
      [ ! -d ./${src_dir} ] \
          && echo "Directory ${src_dir} not present" \
          && exit 1
  done

  if [ -z ${ISORT_ARGS+x} ]; then
    ISORT_ARGS="--check-only -l 120 --profile black"
  fi

  isort ${ISORT_ARGS} ${ISORT_SRC_DIRS}
  echo "Done with isort"
fi

# autoflake code
echo "Running autoflake checks..."
autoflake \
    --remove-all-unused-imports \
    --recursive \
    --exclude=__init__.py \
    --remove-unused-variables \
    --check-diff \
    ${LIBS_DIR}
echo "Done with autoflake"

# flake8 code
echo "Running flake8 checks..."
# stop the build if there are Python syntax errors or undefined names
# E9: Syntax errors (e.g., SyntaxError, IndentationError).
# F63: Undefined names (e.g., importing a module that isn't installed).
# F7: Undefined variables or names that aren't recognized.
# F82: Similar issues related to undefined variables.
# E401: Imports are not grouped correctly.
# E402: Module level import not at top of file.
# W503: Line break occurred before a binary operator.
# E501: Line too long (82 > 79 characters).
# F541: f-string is missing placeholders
flake8 . --count --select=E9,F63,F7,F82,E401,E402 --show-source --statistics
flake8 . --count --ignore=F541,E501,W503 --statistics
echo "Done with flake8 checks"
