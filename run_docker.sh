# Define the paths
HOST_RESULTS_DIR="./results"  # Path to the results directory on the host machine
CONTAINER_RESULTS_DIR="/app/results"  # Path to the results directory in the container

# name of the docker
IMAGE_NAME="$1"

# parameters of the docker
PARAMS="${@:2}"

# Run the Docker container with the volume mount
docker run -v "$(pwd)/$HOST_RESULTS_DIR:$CONTAINER_RESULTS_DIR" $IMAGE_NAME $PARAMS