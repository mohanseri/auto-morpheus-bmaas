echo "starting cd build"
#!/bin/bash -ex

# This has to be called from the Jenkinsfile_CD during the Application's CD build

appid="__APP_ID__"
app_name="__APP_NAME"
tag=${version}-${BUILD_NUMBER}
docker_image="${image_registry}:${tag}"
channel="Jenkins-Continuous" # Make this a comma separated list if you want to promote more than 1 channel. ex: "JC, QA"

# Enable buildx and initialize Buildx
docker run --rm --privileged docker/binfmt:a7996909642ee92942dcd6cff44b9b95f08dad64

ln -s "${HOME}/.docker/cli-plugins" "${DOCKER_CONFIG}/cli-plugins"
docker buildx version
docker buildx create --name __APP_NAME --use || true
docker buildx inspect --bootstrap

echo "Building and pushing docker image ${docker_image}"
export DOCKER_BUILDKIT=1

docker buildx build \
    --platform=linux/amd64 \
    -f docker/Dockerfile \
    --target test-image \
    --no-cache \
    --build-arg JFROG_USERNAME="${jfrog_user}" \
    --build-arg JFROG_PASSWORD="${jfrog_passwd}" \
    -t "${docker_image}" \
    --push \
    .

echo "Docker image pushed to ${docker_image}"

#Create and push the artifacts to coreupdate
pip install \
    --extra-index-url https://${jfrog_user}:${jfrog_passwd}@aruba.jfrog.io/aruba/api/pypi/pypi-local/simple \
    --no-cache hpe-ccs-build-tools

INVOKE_ROOT=$(python -c 'import hpe_ccs_build_tools as _; print(_.__path__[0])')

export UPDATECTL_KEY=${coreupdate_key}
export UPDATECTL_USER=${coreupdate_user}
export PATH=$PATH:/home/ubuntu/.local/bin

invoke --search-root ${INVOKE_ROOT} builder.create-artifacts-and-push \
       --artifact-path "${PWD}/deploy" \
       --app "${app_name}" \
       --appid "${appid}" \
       --tag "${tag}" \
       --docker-image "${docker_image}" \
       --channel "${channel}" \
       --push True