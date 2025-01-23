FROM minizinc/minizinc:latest

# Copy everything from the project to /app
COPY . /app

# Set the working directory inside the container
WORKDIR /app

RUN apt-get update \
    && apt-get install -y python3 python3-venv python3-pip

ENV PATH="/app/venv/bin:$PATH"
RUN python3 -m venv venv

RUN python3 -m pip install --no-cache-dir -r requirements.txt


# Install amplpy and all necessary amplpy.modules:
RUN python3 -m amplpy.modules install highs scip gurobi --no-cache-dir # Install modules
RUN python3 -m amplpy.modules activate 212242c2-be85-469e-81a8-d6b114bdec21

# Run the solver script from /app/src
CMD ["python3", "/app/src/solver.py"]