import json
import os
from z3 import *
import logging
from SMT.loggin_config import setup_logger
from timeit import default_timer as timer
import math
from itertools import combinations

def Max(vec):
    max = vec[0]
    for v in vec[1:]:
        max = If(v > max, v, max)
    return max

def generate_smt_lib(num_couriers, num_items, load_sizes, item_sizes, distances,instance, timeout = 300):
    logger = setup_logger("SMT_proj.log", level=logging.DEBUG)

    results_dir = "SMT/SMT2_FILES"
    os.makedirs(results_dir, exist_ok=True)
    start_time = timer()

    logger.info(f"Solution for instance {instance} started.")

    # Define decision variables
    paths = [[[Bool(f"courier_{i}_{j}_{k}") for k in range(num_items+1)] for j in range(num_items+1)] for i in range(num_couriers)]
    order = [Int(f"order{i}") for i in range(num_items)]
    max_dist = Int("max_dist")

    solver = Solver()
    start_time = timer()

    # Constraints on decision variables domains
    for i in range(num_items):
        solver.add(And(order[i] >= 0, order[i] <= num_items-1))

    # Each customer should be visited only once
    for i in range(num_couriers):
        for k in range(num_items):
            solver.add(Implies(Sum([paths[i][j][k] for j in range(num_items+1)]) == 1, Sum([paths[i][k][j] for j in range(num_items+1)]) == 1))
    
    for k in range(num_items):      
        solver.add(And(Sum([paths[i][j][k] for i in range(num_couriers) for j in range(num_items + 1)]) == 1,
            Sum([paths[i][k][j] for j in range(num_items + 1) for i in range(num_couriers)]) == 1))
    
    # Subtour constraint
    for i in range(num_couriers):
        for j in range(num_items):
            for k in range(num_items):
                solver.add(Implies(paths[i][j][k], order[j] < order[k]))
    
    # Capacity constraint
    for i in range(num_couriers):
        total_load = Sum([paths[i][j][k] * item_sizes[k] for j in range(num_items+1) for k in range(num_items)])
        solver.add(total_load <= load_sizes[i])

    # paths[i][j][j] should be False for any i and any j
    solver.add(Sum([paths[i][j][j] for j in range(num_items+1) for i in range(num_couriers)]) == 0)
    # Each path should begin and end at the depot
    for i in range(num_couriers):
        solver.add(And(Sum([paths[i][num_items][k] for k in range(num_items)]) == 1, Sum([paths[i][j][num_items] for j in range(num_items)]) == 1))

    # Define the objective function
    #solver.add(max([Sum([paths[i][j][k] * distances[j][k] for j in range(num_items+1) for k in range(num_items+1)]) for i in range(num_couriers)]))

    sums = [Sum([paths[i][j][k] * distances[j][k]
             for j in range(num_items+1)
             for k in range(num_items+1)])
        for i in range(num_couriers)]

    # Crea l'espressione che rappresenta il massimo fra tutte queste somme:
    max_expr = Max(sums)

    # Impone che max_dist sia uguale a max_expr:
    solver.add(max_dist == max_expr)


    # Calculation of lower and upper bounds
    num_nodes = num_items + 1
    depot = num_nodes - 1
    lower_bound = max([distances[depot][j] + distances[j][depot] for j in range(num_nodes - 1)])
    upper_bound = max([distances[depot][indices[0]] +
                        sum([distances[indices[i]][indices[i+1]] for i in range(num_items - num_couriers)]) +
                        distances[indices[num_items - num_couriers]][-1]
                        for indices in combinations(range(num_items), num_items - num_couriers + 1)])
      
    # max_distances = [max(distances[i][:-1]) for i in range(num_items)]
    # max_distances.sort()
    # upper_bound = sum(max_distances) + max(distances[depot]) + max([distances[j][depot] for j in range(num_items)])
    

    solver.add(max_dist >= lower_bound)
    solver.add(max_dist <= upper_bound)

    end_time = timer()
    
    if end_time - start_time <= timeout:
        try:
            smt2_model = solver.sexpr().split('\n')
            smt2_model.append("(check-sat)")
            smt2_model.append("(get-value (max_dist))")
            for c in range(num_couriers):
                for j in range(num_nodes):
                    for k in range(num_nodes):
                        smt2_model.append(f"(get-value (courier_{c}_{j}_{k}))")
            logger.debug(f"SMT2 model for instance {instance} generated successfully.")

            smt2_content = "\n".join(smt2_model)
            smt2_path = os.path.join(results_dir, f'{instance}.smt2')
            with open(smt2_path, "w") as f:
                f.write("(set-logic ALL)\n")
                f.write("(set-option :produce-models true)\n")
                f.write(smt2_content)

            logger.info(f"SMT2 file created at {smt2_path} for instance {instance}.")
        except Exception as e:
            logger.error(f"Error processing instance {instance}: {e}", exc_info=True)




if __name__ == "__main__":
    generate_smt_lib()
