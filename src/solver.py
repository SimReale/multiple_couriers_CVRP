import os, sys
import argparse
import check_solution
from CP.solver import solve as cp_solve
from SAT.solver import solve as sat_solve
#from SMT.solver import solve as smt_solve
from MIP.solver import solve as mip_solve

def run_models(instances, approaches, solver_name= None, model_name= None, timeout= 300):
    #run the selected instance using the chosen approach

    RESULTS_DIR = "/app/res/"

    approach_map = {
        'CP' : cp_solve,
        'SAT' : sat_solve, 
        #'SMT' : smt_solve,
        'MIP' : mip_solve
    }

    try:
        
        for approach in approaches:
            if not os.path.exists(RESULTS_DIR + approach):
                os.makedirs(RESULTS_DIR + approach)

            approach_map[approach.upper()](instances, solver_name, model_name)

    except:
        print('\nIncorrect parameters given\n')

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Manage script parameters with required and optional values.")

    parser.add_argument("--instances", type=str, help="Name of the instance(s) seprated by a comma")
    parser.add_argument("--approach", type=str, help="Selected approach to use.")
    parser.add_argument("--solver_name", type=str, help="Name of the solver.")
    parser.add_argument("--model_name", type=str, help="Name of the model.")
    parser.add_argument("--timeout", type=int, help="Timeout in seconds.")

    args = parser.parse_args()

    if args.instances:
        instances = [f'{inst}.dat' for inst in args.instances.split(',')]  
    else:
        directory = 'instances'
        instances = os.listdir(directory)
        instances.sort()
    if args.approach:
        approaches = [args.approach]  
    else:
        approaches = [
                    'CP',
                    #'SAT', 
                    #'SMT', 
                    'MIP'
                    ]

    solver_name = [args[2]] if args.solver_name else args.solver_name
    model_name = [args[3]] if args.model_name else args.model_name

    print(solver_name, model_name)


    run_models(instances, approaches, solver_name, model_name, args.timeout)
        

    check_solution.main(('check_solution', 'instances', 'res/'))