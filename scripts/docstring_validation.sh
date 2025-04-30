#!/bin/bash

# Directory to search for Python files (default is the current directory)
DIR="hpe_morpheus_automation_libs"

# Run pydocstyle on the directory
echo "Running pydocstyle on Python files in $DIR ..."
pydocstyle --ignore D200,D203,D212,D213,D400,D401,D403,D404,D104,D415,D205 $DIR

# Capture exit code to determine if pydocstyle found any issues
exit_code=$?

# Exit with the appropriate code
if [ $exit_code -ne 0 ]; then
    echo "pydocstyle found issues with docstrings."
    exit 1
else
    echo "No issues found with docstrings."
    exit 0
fi
