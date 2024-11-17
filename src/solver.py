from minizinc import Instance, Model, Solver
import json, os
from datetime import timedelta

current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)
new_directory = os.path.join(parent_dir, 'results')

if not(os.path.isdir(new_directory)):
    os.makedirs(new_directory)

path = "CP/data"
instances = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
instances.sort()

#TODO iterate over all the instances, maybe create more solver, one for each approach...
model = Model("CP/CP_proj.mzn")
gecode = Solver.lookup("gecode")
inst = Instance(gecode, model)
inst.add_file('CP/data/inst01.dzn')#instances could be transformed even into json files, mzn files are able to read it (https://stackoverflow.com/questions/62893987/how-to-read-from-dzn-file-without-variable-names-in-minizinc)
#print(gecode.version) #i have check the version is 6.3.0
timelimit = timedelta(minutes=1)
result = inst.solve(timeout=timelimit)#timelimit needs to be a timedelta (https://python.minizinc.dev/en/latest/api.html#solvers)

result_data = {
    "objective": result.objective,
    "variables": result.solution.__dict__
}

result_json = json.dumps(result_data, indent=4)
#print(result_json)

new_directory = os.path.join(parent_dir, 'results/CP')
if not(os.path.isdir(new_directory)):
    os.makedirs(new_directory)
os.chdir(new_directory)

with open("result.json", "w") as json_file:
    json.dump(result_json, json_file, indent=4)
print('the docker work, everything is fine, go eat!')