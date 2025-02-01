FROM minizinc/minizinc:latest

# Copy everything from the project to /app
COPY . /app

# Set the working directory inside the container
WORKDIR /app

RUN apt-get update \
    && apt-get install -y python3 python3-venv python3-pip

VOLUME /app/res/

ENV PATH="/app/venv/bin:$PATH"
RUN python3 -m venv venv

RUN python3 -m pip install --no-cache-dir -r requirements.txt


RUN apt-get update && apt-get install -y cvc5
RUN apt-get update && apt-get install -y cvc4


# Install amplpy and all necessary amplpy.modules:
RUN python3 -m amplpy.modules install highs scip gurobi --no-cache-dir
RUN python3 -m amplpy.modules activate 43867611-2cd2-402b-8fb0-aa4768edcd50

# Run the solver script
ENTRYPOINT ["python3", "/app/solver.py"]