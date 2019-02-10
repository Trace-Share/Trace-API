
if [ -z "$DOCKER_UID" ]; then
    DOCKER_UID=$(id -u)
fi

if [ -z "$DOCKER_GID" ]; then
    DOCKER_GID=$(id -g)
fi

docker build --build-arg UID=$DOCKER_UID --build-arg GID=$DOCKER_GID -t trace-tools ext/.
