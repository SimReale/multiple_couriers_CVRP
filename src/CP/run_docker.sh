#!/bin/bash


# Define variables
IMAGE_NAME="cdmo:latest"
RESULTS_DIR=$(pwd)/results
MODELS_DIR=$(pwd)/src/CP
DOCKERFILE=$(pwd)/Dockerfile
LAST_BUILD_FILE=".last_build"
SOLVER_FILE=$(pwd)/src/solver.py

function needs_rebuild() {
    if [ ! -f "$LAST_BUILD_FILE" ]; then
        # If there's no record of the last build, we need to build
        return 0
    fi

    LAST_BUILD=$(cat "$LAST_BUILD_FILE")

    # Check if the Dockerfile was modified after the last build
    if [ "$(stat -f "%m" "$DOCKERFILE")" -gt "$LAST_BUILD" ]; then
        return 0
    fi

    # Check if any model in the models directory was modified after the last build
    for MODEL_FILE in "$MODELS_DIR"/*.mzn; do
        if [ -f "$MODEL_FILE" ] && [ "$(stat -f "%m" "$MODEL_FILE")" -gt "$LAST_BUILD" ]; then
            return 0
        fi
    done

    # Check if the solver file was modified after the last build
    if [ -f "$SOLVER_FILE" ] && [ "$(stat -f "%m" "$SOLVER_FILE")" -gt "$LAST_BUILD" ]; then
        return 0
    fi

    return 1
}

# Check if rebuild is necessary
if needs_rebuild; then
    echo "Building Docker image..."
    docker build -t "$IMAGE_NAME" .
    date +%s > "$LAST_BUILD_FILE"
else
    echo "Docker image is up to date. Skipping build."
fi

# Create the results directory if not exists
if [ ! -d "$RESULTS_DIR" ]; then
    echo "Creating results directory..."
    mkdir -p "$RESULTS_DIR"
fi

# Run the Docker container
echo "Running the Docker container..."
docker run -it \
  -v "$RESULTS_DIR:/app/results" \
  "$IMAGE_NAME"