#FROM minizinc/minizinc:final #debian has updated the terms we cannot modify the system with pip install -> i should create my own venv, not good -> i have down to version 2.8.3 (not a problem, it works)
FROM minizinc/minizinc:2.8.3 

# install python and all the dependencies
RUN apt-get update -y \
    && apt-get install -y python3 \
    && apt-get install -y python3-pip 

# set a directory for the app
#WORKDIR /src
WORKDIR /
# copy all the files to the container
COPY . .  

RUN python3 -m pip install -r requirements.txt

# run the command
CMD ["python3", "solver.py"]