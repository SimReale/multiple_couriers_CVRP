import os, sys
import check_solution
from CP.solver import solve as cp_solve
from SAT.solver import solve as sat_solve
#from SMT.solver import solve as smt_solve
from MIP.solver import solve as mip_solve

def run_models(instances, approaches, solver_name= None, model_name= None, timeout= 300):
    #run the selected instance using the chosen approach

    RESULTS_DIR = "/app/results/"

    approach_map = {
        'CP' : cp_solve,
        'SAT' : sat_solve, 
        #'SMT' : smt_solve,
        'MIP' : mip_solve
    }

    for approach in approaches:
            #create results directory
            if not os.path.exists(RESULTS_DIR + approach):
                os.makedirs(RESULTS_DIR + approach)

<<<<<<< HEAD
            print(approach_map[approach])

            approach_map[approach](instances, solver_name, model_name)

    try:
        
        '''for approach in approaches:
            #create results directory
            if not os.path.exists(RESULTS_DIR + approach):
                os.makedirs(RESULTS_DIR + approach)

            print(approach_map[approach])

            approach_map[approach](instances, solver_name, model_name)'''
=======
            approach_map[approach](instances, solver_name, model_name)
>>>>>>> 20a7eaa514990323662469446a8b047df4c11523

    except:
        print('\nIncorrect parameters given\n')

if __name__ == "__main__":

    args = sys.argv[1:]

    if not args:
        
        directory = 'instances'
        instances = os.listdir(directory)
        instances.sort()
        approaches = [
                      #'CP',
                      #'SAT', 
                      #'SMT', 
                      'MIP'
                      ]
        run_models(instances, approaches)

    else:

        instances_name = [f'{inst}.dat' for inst in args[0].split(',')]
        approach = [args[1].upper()]
        solver_name = [args[2]]
        model_name = [args[3]]

        run_models(instances_name, approach, solver_name, model_name)

    check_solution.main(('check_solution', 'instances', 'results/'))