#!/bin/bash -x

# This has to be called from the Jenkinsfile_CD during the Application's CD build

appid="__APP_NAME"
app_name="__APP_ID__"
tag=${version}-${BUILD_NUMBER}
docker_image="${image_registry}:${tag}.dev"
#channel="PR" # Make this a comma separated list if you want to promote more than 1 channel. ex: "JC, QA"
channel="PR" # Make this a comma separated list if you want to promote more than 1 channel. ex: "JC, QA"

# Build the docker image
echo "Building the docker image ${docker_image}"
docker build -t "${docker_image}" --target test-image -f docker/Dockerfile --no-cache --build-arg JFROG_USERNAME="${jfrog_user}" --build-arg JFROG_PASSWORD="${jfrog_passwd}" .

# Load the trust Key
echo "Loading Trust Key"
docker trust key load "${dct_pvt_key}"

#Create a trust key folder
mkdir -p "${DOCKER_CONFIG}/trust/private"
cp "${dct_pvt_key}" "${DOCKER_CONFIG}/trust/private/${dct_file_name}.key"

docker trust inspect --pretty "${docker_image}" || true
docker trust revoke "${docker_image}" || true

#Sign and push the image
echo "Pushing the image ${docker_image}"
docker trust sign "${docker_image}"

docker rmi -f "${docker_image}"