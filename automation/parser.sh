#!/bin/bash -x

# Exporting clusterundertest and testtype env variables

export ClusterUnderTest=$(jq -r ".clusterinfo.INPUTENV.CLUSTERUNDERTEST" /configmap/data/infra_clusterinfo.json)
export TestType=$(jq -r ".clusterinfo.INPUTENV.TESTTYPE" /configmap/data/infra_clusterinfo.json)
export S3Path=$(jq -r ".clusterinfo.INPUTENV.TESTTYPE" /configmap/data/infra_clusterinfo.json)
export AppNamespaceSuffix=$(jq -r ".clusterinfo.INPUTENV.APPNAMESPACESUFFIX" /configmap/data/infra_clusterinfo.json)
