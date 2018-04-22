#!/bin/bash

DOCKER_REGISTRY=retrocontestajvidhoekmrcpqzt.azurecr.io

ACTION=$1
AGENT_FOLDER=$2
AGENT_VERSION=$3

if [[ -z "$ACTION" ]]; then
  echo "Error: please provide first [build|test|push] parameter, e.g. build_docker.sh build"
  exit 1
elif [[ -z "$AGENT_FOLDER" ]] || [[ -z "$AGENT_VERSION" ]]; then
  echo "Error: please provide <folder> <version>, e.g. build_docker.sh build random-agent v3"
  exit 1
fi

if [[ "$ACTION" == "build" ]]; then
  echo "Building agent for Docker submission..."
  cd $AGENT_FOLDER
  docker build -f box.docker -t $DOCKER_REGISTRY/$AGENT_FOLDER:$AGENT_VERSION .
  cd -

elif [[ "$ACTION" == "test" ]]; then
  echo "Testing agent as remote Docker submission..."
  retro-contest run --agent $DOCKER_REGISTRY/$AGENT_FOLDER:$AGENT_VERSION \
    --results-dir results --no-nv --use-host-data SonicTheHedgehog-Genesis GreenHillZone.Act1

elif [[ "$ACTION" == "push" ]]; then
  echo "Pushing agent to OpenAI repository..."
  docker push $DOCKER_REGISTRY/$AGENT_FOLDER:$AGENT_VERSION

fi


