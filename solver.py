from minizinc import Instance, Model, Solver
import json, os
from datetime import timedelta
import time
from src import check_solution


current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)
new_directory = 'results/CP'
if not(os.path.isdir(new_directory)):
    os.makedirs(new_directory)

os.chdir('src')
directory = 'CP/data'

# List all elements in the directory
instances = os.listdir(directory)
instances.sort()
# Print the elements
for el in instances[:1]:

    #TODO create more solver, one for each approach...
    
    model_name = "gecode"
    model = Model("CP/CP_proj.mzn")

    gecode = Solver.lookup("gecode")
    inst = Instance(gecode, model)
    inst.add_file(f'{directory}/{el}')#instances could be transformed even into json files, mzn files are able to read it (https://stackoverflow.com/questions/62893987/how-to-read-from-dzn-file-without-variable-names-in-minizinc)
    #print(gecode.version) #i have check the version is 6.3.0
    timelimit = timedelta(minutes=5)


    result = inst.solve(timeout=timelimit) #timeout needs to be a timedelta (https://python.minizinc.dev/en/latest/api.html#solvers)
    
    #getting the time to solve in seconds
    solve_time = result.statistics['solveTime'].seconds


    #no solution found -> file json not created
    if result.status != result.status.UNKNOWN:
        path_matrix = result.solution.x
        result_path = []
        for r in range(len(path_matrix)):
            courier_path = [path_matrix[r][len(path_matrix[r])-1]]
            while path_matrix[r][courier_path[-1]-1] != len(path_matrix[r]):
                courier_path.append(path_matrix[r][courier_path[-1]-1])
            result_path.append(courier_path)

        result = {
            "gecode" : 
            {
                "time" : solve_time,
                "optimal" : result.status == result.status.OPTIMAL_SOLUTION and solve_time < 300,
                "obj" : result.objective,
                "sol" : result_path
            }
        }

        os.chdir('../results/CP')

        with open(f"{el.removesuffix('.dzn')}.json", "w") as json_file:
            json.dump(result, json_file, indent=4)

        
        os.chdir('../../src')


os.chdir('../')
check_solution.main(('check_solution', 'src/instances', 'results/'))