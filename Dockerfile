# Use Minizinc Docker image version 2.8.4
FROM minizinc/minizinc:2.8.4

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

# Run the solver script from /app/src
CMD ["python3", "/app/src/solver.py"]