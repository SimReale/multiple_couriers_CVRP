from minizinc import Instance, Model, Solver
import json, os
from datetime import timedelta
import time
import check_solution

print('Starting solver...')

# Define the directory for storing results
RESULTS_DIR = "/app/results/CP"

if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)
    print(f"Created results directory: {RESULTS_DIR}")

SRC_DIR = "/app/src"
os.chdir(SRC_DIR)

DATA_DIR = "CP/data"
instances = sorted(os.listdir(DATA_DIR))

for el in instances:
    print(f"Solving instance: {el}")
    
    model = Model("CP/CP_proj.mzn")
    gecode = Solver.lookup("gecode")
    inst = Instance(gecode, model)
    
    inst.add_file(f"{DATA_DIR}/{el}")
    # Time limit of 5 minutes for solving
    timelimit = timedelta(minutes=5)

    # Solve the instance
    result = inst.solve(timeout=timelimit)
    solve_time = result.statistics['solveTime'].seconds

    # Extract the solution matrix
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

        result_filename = f"{RESULTS_DIR}/{el.removesuffix('.dzn')}.json"
        with open(result_filename, "w") as json_file:
            json.dump(result, json_file, indent=4)
        
        print(f"Saved result to {result_filename}")

print("Solver completed.")
print("Check solution started")
check_solution.main(('check_solution', 'instances', '../results/'))
print("Check solution finished.")
