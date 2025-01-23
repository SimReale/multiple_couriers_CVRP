from amplpy import AMPL, add_to_path
import os
import math
import check_solution 
import json
import time
import multiprocessing

def instance_converter():
    #read instances
    directory = 'instances'
    instances = os.listdir(directory)
    instances.sort()
    for instance in instances:
        with open(directory + '/' + instance) as file:
            data = file.read().strip().splitlines()
        
        output_lines = []
        output_lines.append(f"param m := {int(data[0])};\n\n")
        output_lines.append(f"param n := {int(data[1])};\n\n")
        
        output_lines.append(f"param l :=\n") #courier capacity
        for idx, dat in enumerate (data[2].split(), 1):
            output_lines.append(f'{idx} {dat}\n') 
        output_lines.append(';\n\n')
        
        output_lines.append(f"param s :=\n") #size items
        for idx, dat in enumerate (data[3].split(), 1):
            output_lines.append(f'{idx} {dat}\n')
        output_lines.append(';\n\n')

        output_lines.append(f'param D : ')
        for i in range(1, int(data[1])+2):
            output_lines.append(f'{i} ')
        output_lines.append(':=\n')
        for i in range(1, int(data[1])+2):
            output_lines.append(f'{i} ')
            for idx, j in enumerate(data[4+i-1].split()):
                if idx == int(data[1]):
                    output_lines.append(f'{j}')
                else:
                    output_lines.append(f'{j} ')
            output_lines.append(f'\n')
        output_lines.append(';')

        #convert them into readable file for ampl
        output_directory = "src/MIP/instances"
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        output_file_path = os.path.join(output_directory, f"{instance}")
        with open(output_file_path, "w") as output_file:
            output_file.writelines(output_lines)

def solve():

    instance_converter()
    
    RESULTS_DIR = "results/MIP"

    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
        print(f"Created results directory: {RESULTS_DIR}")

    timeout = 300

    directory = 'src/MIP/instances'
    instances = os.listdir(directory)
    instances.sort()

    solvers = [
    'scip', 
    'highs',
    #'gurobi'
    ]
    models = os.listdir('MIP/models')
    models = ['ampl.mod']
    #instances = [instances[i] for i in range(len(instances)) if i in [12, 15, 18]]
    for inst in instances:
        results = {}

        for model_name in models:
            for solver in solvers:
            
                # Create an AMPL instance
                ampl = AMPL()
                # Read the model and data files.
                ampl.read(f"MIP/models/{model_name}")
                ampl.read_data(f"{directory}/{inst}")

                ampl.set_option('solver', solver)
                ampl.set_option(solver + '_options', f'timelimit= {timeout}')
                ampl.set_option('randseed', 42)

                # solve and check the time
                start_time = time.time()
                ampl.solve()
                end_time = time.time()
                solve_time = math.floor(end_time-start_time)

                solve_result = ampl.getValue('solve_result')
                
                #get result
                if solve_result == 'solved' or solve_result == 'limit':

                    obj = round(ampl.getValue("max_distance"))
                    x = ampl.getVariable('x')
                    m = ampl.getValue('m')
                    n = ampl.getValue('n')
                    
                    sol = []
                    for couriers in range(1,m+1):
                        couriers_packs = []
                        packs = n + 1
                        while round(x[packs, n+1, couriers].value()) == 0:
                            for i in range(1, n + 1):
                                if round(x[packs, i, couriers].value()) == 1:
                                    couriers_packs.append(i)
                                    packs = i
                                    break
                        sol.append(couriers_packs)

                    results[model_name.removesuffix('.mod')+"_"+solver] = {
                        "time" : solve_time if solve_result == 'solved' else timeout,
                        "optimal" : solve_result == 'solved' and solve_time < timeout,
                        "obj" : obj,
                        "sol" : sol
                        }

                    print(f'instance: {inst} {model_name.removesuffix(".mod")+"_"+solver}: {results[model_name.removesuffix(".mod")+"_"+solver]}\n')
                
                else:
                    results[model_name.removesuffix('.mod')+"_"+solver] = {
                        "time": timeout,
                        "optimal": False,
                        "obj": None,
                        "sol": None
                    }

        result_filename = f"{RESULTS_DIR}/{inst.removesuffix('.dat')}.json"
        with open(result_filename, "w") as json_file:
            json.dump(results, json_file, indent=4)

if __name__ == "__main__":
    solve()