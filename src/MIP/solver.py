from amplpy import AMPL, add_to_path
import os
import math
import json
import time

def instance_converter(instance_number= None):
    #read instances
    directory = 'instances'
    instances = os.listdir(directory)
    instances.sort()
    if instance_number:
        instances = instances[int(instance_number)-1:int(instance_number)]

    output_directory = "MIP/instances"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

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

        output_file_path = os.path.join(output_directory, f"{instance}")
        with open(output_file_path, "w") as output_file:
            output_file.writelines(output_lines)

def solve(instance_number= None, model_name= None, solver_name= None, timeout = 300):

    instance_converter(instance_number)

    #time.sleep(100)

    directory = 'MIP/instances'
    instances = os.listdir(directory)
    instances.sort()

    if solver_name:
        solvers = [solver_name]
    else:
        solvers = [
        'scip', 
        'highs',
        'gurobi'
        ]

    if model_name:
        models = [model_name]
    else:
        models = os.listdir('MIP/models')

    models = [mod for mod in models if mod != 'two_index.mod']

    for inst in instances:

        results = {}
        for mdl in models:
            for solver in solvers:
                # Create an AMPL instance
                ampl = AMPL()
                # Read the model and data files.
                ampl.read(f"MIP/models/{mdl}")
                ampl.read_data(f"{directory}/{inst}")

                ampl.set_option('solver', solver)
                if solver in ['gurobi', 'highs']:
                    ampl.set_option(solver + '_options', f'threads= 1 timelimit= {timeout}')
                else:
                    ampl.set_option(solver + '_options', f'timelimit= {timeout}')
                ampl.set_option('randseed', 42)

                # solve and check the time
                start_time = time.time()
                ampl.solve()
                end_time = time.time()
                solve_time = math.floor(end_time-start_time)

                solve_result = ampl.getValue('solve_result')
                obj = round(ampl.getValue("max_distance"))
                x = ampl.getVariable('x')
                m = ampl.getValue('m')
                n = ampl.getValue('n')

                if solve_result in ["infeasible", "unbounded"] or obj == 0.0:
                    results[mdl.removesuffix('.mod')+"_"+solver] = {
                        "time": timeout,
                        "optimal": False,
                        "obj": None,
                        "sol": None
                    }
                
                else:
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

                    results[mdl.removesuffix('.mod')+"_"+solver] = {
                        "time" : solve_time if solve_result == 'solved' else timeout,
                        "optimal" : solve_result == 'solved' and solve_time < timeout,
                        "obj" : obj,
                        "sol" : sol
                        }

                    print(f'instance: {inst} {mdl.removesuffix(".mod")+"_"+solver}: {results[mdl.removesuffix(".mod")+"_"+solver]}\n')

        result_filename = f"results/MIP/{inst.removesuffix('.dat')}.json"
        with open(result_filename, "w") as json_file:
            json.dump(results, json_file, indent=4)

if __name__ == "__main__":
    solve()