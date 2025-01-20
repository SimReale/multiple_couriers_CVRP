from amplpy import AMPL, add_to_path
import os
import pandas as pd
import math
import check_solution 
import json
import time

def instance_converter():
    #read instances
    directory = 'src/instances'
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

def main():

    instance_converter()
    
    RESULTS_DIR = "results/MIP"

    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
        print(f"Created results directory: {RESULTS_DIR}")

    timeout = 300

    directory = 'src/MIP/instances'
    instances = os.listdir(directory)
    instances.sort()

    for inst in instances[12:13]:

        # Create an AMPL instance
        ampl = AMPL()
        # Read the model and data files.
        ampl.read(f"src/MIP/ampl.mod")
        ampl.read_data(f"{directory}/{inst}")
        
        solver = 'highs'
        
        ampl.setOption('solver', solver)
        ampl.setOption(solver + '_options', f'timelimit={timeout}')
        ampl.setOption('randseed', 42)

        # Solve
        start_time = time.time()
        ampl.solve()
        end_time = time.time()
        solve_time = min(300, int(end_time-start_time))
        #solve_time = math.floor(ampl.get_value("_solve_elapsed_time"))

        '''if ampl.solve_result != "solved":
            raise Exception(f"Failed to solve (solve_result: {ampl.solve_result})")'''
        
        solved_value = ampl.getValue('solve_result')
        if solved_value == 'solved' or solved_value == 'limit':
            #Get the values of the variable Buy in a dataframe object
            obj = round(ampl.getValue("max_distance"))

            x = ampl.get_variable("x")
            x = x.get_values()
            x = x.to_dict()

            with open('src/instances' + '/' + inst) as file:
                data = file.read().strip().splitlines()

            m = int(data[0])
            n = int(data[1])
            
            sol = {}
            for c in range(1, m + 1):
                start = n+1
                for i in range(1, n+1):
                    val = round(x[(start, i, c)], 2)
                    if val == 1:
                        start = i
                        sol[c] = []
                        break

                i = 1
                while True:
                    val = round(x[(start, i, c)], 2)
                    if val == 1:
                        sol[c].append(start)
                        start = i
                    i += 1
                    if start == n+1:
                        break
                    if i>n+1:
                        i = 1

            result = {
                'highs' : 
                {
                    "time" : solve_time,
                    "optimal" : ampl.getValue('solve_result') == 'solved' and solve_time < timeout,
                    "obj" : obj,
                    "sol" : list(sol.values())
                }
            }
            print(f'instance: {inst}: {result}\n')

            result_filename = f"{RESULTS_DIR}/{inst.removesuffix('.dat')}.json"
            with open(result_filename, "w") as json_file:
                json.dump(result, json_file, indent=4)

    check_solution.main(('check_solution', 'src/instances', 'results/'))

if __name__ == "__main__":
    main()