from minizinc import Instance, Model, Solver
import json, os
from datetime import timedelta
import time
import check_solution
import sys
from CP.solver import solve as cp_solve
from SAT.solver import solve as sat_solve
#from SMT.solver import solve as smt_solve
from MIP.solver import solve as mip_solve

def run_all():
    #run all the instances with all the approaches

    # Define the directory for storing results
    RESULTS_DIR = "/app/results/"
    approaches = ['CP', 'SAT', 'SMT', 'MIP']

    for approach in approaches:
        if not os.path.exists(RESULTS_DIR + approach):
            os.makedirs(RESULTS_DIR + approach)
            print(f"Created results directory: {RESULTS_DIR + approach}")

    #cp_solve()
    sat_solve()
    #mip_solve()

def run_selected(instance_number, approach, solver_name):
    #run the selected instance using the chosen approach
    print('well arrived in the hell')
    approach_map = {
        'CP' : cp_solve,
        #'SAT' : sat_solve, 
        #'SMT' : smt_solve,
        'MIP' : mip_solve
    }
    RESULTS_DIR = "/app/results/"
    
    try:

        if not os.path.exists(RESULTS_DIR + approach):
            os.makedirs(RESULTS_DIR + approach)

        approach_map[approach](instance_number, solver_name)

    except:
        print('Incorrect parameters given')

if __name__ == "__main__":

    args = sys.argv[1:]

    #moving to the current working directory
    SRC_DIR = "/app/src"
    os.chdir(SRC_DIR)
    print(args)

    if not args:
        run_all()
    else:
        run_selected(args[0], args[1].upper(), args[2])

    print("Solver completed.")
    print("Check solution started")
    check_solution.main(('check_solution', 'instances', '../results/'))
    print("Check solution finished.")