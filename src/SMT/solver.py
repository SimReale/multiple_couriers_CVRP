from SMT.smt_model import *
from SMT.smt_lib_core import generate_smt_lib
from SMT.solver_smtlib import solve as solve_smtlib
from time import sleep
import re



def solve(instances, solver_name, model_name= None, timeout=300):
    
    if solver_name:
        solvers = solver_name
    else:
        solvers = ['z3_py','z3','cvc4','cvc5']

    if model_name:
        models = model_name
    else:
        models = ['base','symm']


    for inst in instances:

        number = re.search(r'\d+', inst)
        instance_number = int(number.group())

        results = {}
        m, n, L, S, D = process_instance(inst)
        if instance_number <= 10:
            generate_smt_lib(m, n, L, S, D, instance_number, timeout) 

        for solver in solvers:
            if solver == 'z3_py':
                for model in models: 
                    if model == 'base':
                        res = SMT_model(m, n, L, S, D, False, timeout)
                        results[f'{model}_{solver}'] = res  
                    if model == 'symm': 
                        res = SMT_model(m, n, L, S, D, True, timeout) 
                        results[f'{model}_{solver}'] = res 

            else:
                results[solver] = solve_smtlib(instance_number,solver)
                
        result_filename = f"res/SMT/{instance_number}.json"
        with open(result_filename, "w") as json_file:
            json.dump(results, json_file, indent=4)


if __name__ == "__main__":
    solve()
