from minizinc import Instance, Model, Solver
import json, os
from datetime import timedelta
import time

#created the results directory
print('ok1')
current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)
new_directory = 'results/CP'
if not(os.path.isdir(new_directory)):
    os.makedirs(new_directory)
print('ok2')
os.chdir('src')
directory = 'CP/data'

# List all elements in the directory
instances = os.listdir(directory)
instances.sort()
# Print the elements
for el in instances[:10]:
    print('ok3')
    #TODO create more solver, one for each approach...
    
    model_name = "gecode"
    model = Model("CP/CP_proj.mzn")

    gecode = Solver.lookup("gecode")
    inst = Instance(gecode, model)
    inst.add_file(f'{directory}/{el}')#instances could be transformed even into json files, mzn files are able to read it (https://stackoverflow.com/questions/62893987/how-to-read-from-dzn-file-without-variable-names-in-minizinc)
    #print(gecode.version) #i have check the version is 6.3.0
    timelimit = timedelta(minutes=5)

    start = time.time()
    result = inst.solve(timeout=timelimit) #timeout needs to be a timedelta (https://python.minizinc.dev/en/latest/api.html#solvers)
    end_time = time.time() - start

    #round to integer
    end_time = int(end_time)

    path_matrix = result.solution.__dict__['x']
    result_path = []
    for r in range(len(path_matrix)):
        courier_path = [path_matrix[r][len(path_matrix[r])-1]]
        while path_matrix[r][courier_path[-1]-1] != len(path_matrix[r]):
            courier_path.append(path_matrix[r][courier_path[-1]-1])
        result_path.append(courier_path)

    result = {
        "gecode" : 
        {
            "time" : end_time,
            "optimal" : end_time < 300,
            "obj" : result.objective,
            "sol" : result_path
        }
    }


    result_json = json.dumps(result, indent=4)

    os.chdir('../results/CP')

    with open(f"{el.removesuffix('.dzn')}.json", "w") as json_file:
        json.dump(result_json, json_file, indent=4)

    
    os.chdir('../../src')