#!/bin/bash
CONTAINER_NAME="reports-checker"
CONTAINER_PORT="8079"

docker build -t $CONTAINER_NAME:latest -f docker/Dockerfile.LEN .

CONTAINER_EXISTS=$(docker ps -a --format '{{.Names}}' --filter "name=^$CONTAINER_NAME$" | wc -w);

if  [ $CONTAINER_EXISTS != 0 ] ; then
	docker container stop "$CONTAINER_NAME";
	docker container rm "$CONTAINER_NAME";
else
	echo "Container $CONTAINER_NAME does not exist";
fi

docker run -p $CONTAINER_PORT:8000 -d --name $CONTAINER_NAME --mount type=bind,source=/etc/hosts,target=/etc/hosts,readonly $CONTAINER_NAME