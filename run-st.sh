#!/bin/bash -x

set -e

current_path=${PWD}
pushd /opt/ccs/automation

file="poetry.lock"

if [ -f "$file" ] ; then
    rm "$file"
fi

running_cm=`cat /configmap/data/infra_clusterinfo.json`
echo "running with configmap: " $running_cm

# Generate spec will install all python libs as well
./generate_spec.sh ${current_path}
popd

pip3 install playwright
playwright install-deps
playwright install chromium
pip uninstall pytest-randomly -y

source /opt/ccs/automation/parser.sh
echo "cluster under test"
echo $ClusterUnderTest
echo "================="
rm -rf /tmp/results || true

export PYTHONPATHORIG="${PYTHONPATH}"
export PYTHONPATH="${PYTHONPATHORIG}:/opt/ccs/automation/"

mkdir -p /tmp/results/testrail

## test case paths here
poetry run pytest --alluredir /tmp/results tests/examples/brownfield/ExistingAcctNewDevices/ -v -s -m ${TestType}  || true

## change directory to automation_svc_ui and run test cases with svc-centric_ui branch cases
unset PYTHONPATH
pushd /opt/ccs/automation_svc_ui
export PYTHONPATH="${PYTHONPATHORIG}:/opt/ccs/automation_svc_ui/"

poetry run pytest --alluredir /tmp/results tests/examples/brownfield/ExistingAcctNewDevices/ -v -s -m ${TestType}  || true

poetry run python /opt/ccs/automation/.venv/lib/python3.8/site-packages/hpe_glcp_automation_lib/libs/commons/utils/s3/s3-upload.py
