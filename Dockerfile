# Use Minizinc Docker image version 2.8.3
FROM minizinc/minizinc:2.8.3

# Install Python and pip for additional script dependencies
RUN apt-get update -y \
    && apt-get install -y python3 python3-pip 

# Set the working directory inside the container
WORKDIR /app

# Copy everything from the project to /app
COPY . /app

# Volume for results 
VOLUME /app/results/

# Install dependencies
RUN python3 -m pip install --no-cache-dir -r /app/requirements.txt

# Install amplpy and all necessary amplpy.modules:
RUN python3 -m pip install amplpy --no-cache-dir # Install amplpy
RUN python3 -m amplpy.modules install highs scip gurobi --no-cache-dir # Install modules
RUN python3 -m amplpy.modules activate 212242c2-be85-469e-81a8-d6b114bdec21

# Run the solver script from /app/src
CMD ["python3", "/app/src/solver.py"]