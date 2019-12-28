#!/bin/bash

# PURPOSE: used be jenkins to launch Wall_e to the CSSS TEST Discord Guild

set -e -o xtrace
# https://stackoverflow.com/a/5750463/7734535

rm ${DISCORD_NOTIFICATION_MESSAGE_FILE}

export testContainerDBName="${COMPOSE_PROJECT_NAME}_wall_e_db"
export testContainerName="${COMPOSE_PROJECT_NAME}_wall_e"
export testImageName_lowerCase=$(echo "$testContainerName" | awk '{print tolower($0)}')
export COMPOSE_PROJECT_NAME_lowerCase=$(echo "$COMPOSE_PROJECT_NAME" | awk '{print tolower($0)}')
export DOCKER_COMPOSE_FILE="CI/server_scripts/docker-compose.yml"

if [ "${BRANCH_NAME}" = "master" ]; then
    export ORIGIN_IMAGE="wall_e"
else
    export ORIGIN_IMAGE=$(echo "${COMPOSE_PROJECT_NAME}"_wall_e_base | awk '{print tolower($0)}')
fi


docker rm -f ${testContainerName} ${testContainerDBName} || true
docker network rm ${COMPOSE_PROJECT_NAME_lowerCase}_default || true
docker image rm -f ${testImageName_lowerCase} || true
docker volume create --name="${COMPOSE_PROJECT_NAME}_logs"

docker-compose -f "${DOCKER_COMPOSE_FILE}" up --force-recreate  -d
sleep 20

export containerFailed=$(docker ps -a -f name=${testContainerName} --format "{{.Status}}" | head -1)
export containerDBFailed=$(docker ps -a -f name=${testContainerDBName} --format "{{.Status}}" | head -1)
if [[ "${containerFailed}" != *"Up"* ]]; then
    docker logs ${testContainerName}
    docker logs ${testContainerName} --tail 12 &> ${DISCORD_NOTIFICATION_MESSAGE_FILE}
    exit 1
fi

if [[ "${containerDBFailed}" != *"Up"* ]]; then
    docker logs ${testContainerDBName}
    docker logs ${testContainerDBName} --tail 12 &> ${DISCORD_NOTIFICATION_MESSAGE_FILE}
    exit 1
fi
