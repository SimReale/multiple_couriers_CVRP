FROM minizinc/minizinc:latest

COPY . /app

WORKDIR /app

RUN apt-get update \
    && apt-get install -y python3 python3-venv python3-pip

VOLUME /app/res/

ENV PATH="/app/venv/bin:$PATH"

RUN python3 -m venv venv

RUN python3 -m pip install --no-cache-dir -r requirements.txt


RUN apt-get update && apt-get install -y cvc5
RUN apt-get update && apt-get install -y cvc4
RUN python3 -m amplpy.modules install highs scip gurobi --no-cache-dir
ENV AMPL_LICENSE=""

# Run the solver script
ENTRYPOINT ["python3", "/app/solver.py"]