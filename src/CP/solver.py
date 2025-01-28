from minizinc import Instance, Model, Solver
from datetime import timedelta
import json, os
from CP.parser_CP import parse
import time, math

def solve(instance_number= None, model_name= None, solver_name= None, timeout = 300):

    parse(instance_number)
    DATA_DIR = "CP/data"
    instances = sorted(os.listdir(DATA_DIR))
    if instance_number:
        instances = [inst for inst in instances if instance_number in inst]

    if solver_name:
        solver_list = [solver_name]
    else:
        solver_list = ['gecode',
                       'chuffed'
                       ]

    for inst in instances:
        print(f"Solving instance: {inst}")
        results = {}
        for slv in solver_list:

            if model_name:
                model_list = [model_name]
            else:
                model_list = os.listdir(f'CP/models/{slv}')

            for mdl in model_list:

                model = Model(f'CP/models/{slv}/{mdl}')
                solver = Solver.lookup(slv)
                instance = Instance(solver, model)

                instance.add_file(f"{DATA_DIR}/{inst}")
                # Time limit of 5 minutes for solving
                timelimit = timedelta(seconds=timeout)

                # Solve the instance
                start_time = time.time()
                result = instance.solve(timeout=timelimit)
                end_time = time.time()
                solve_time = math.floor(end_time - start_time)

                # Extract the solution matrix
                if result.status != result.status.UNKNOWN:
                    path_matrix = result.solution.x
                    result_path = []
                    for r in range(len(path_matrix)):
                        courier_path = [path_matrix[r][len(path_matrix[r])-1]]
                        while path_matrix[r][courier_path[-1]-1] != len(path_matrix[r]):
                            courier_path.append(path_matrix[r][courier_path[-1]-1])
                        result_path.append(courier_path)

                    results[mdl] = {
                        "time" : solve_time,
                        "optimal" : result.status == result.status.OPTIMAL_SOLUTION and solve_time < timeout,
                        "obj" : result.objective,
                        "sol" : result_path
                        }

        result_filename = f"results/CP/{inst.removesuffix('.dzn')}.json"
        with open(result_filename, "w") as json_file:
            json.dump(results, json_file, indent=4)