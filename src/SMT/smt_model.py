from z3 import *
from timeit import default_timer as timer
import json
from itertools import combinations


def callback(tmp_model):
    callback.step_counter += 1
    print("=================================")
    print(f"Step number: {callback.step_counter}")


def process_instance(instance):
    """Reads and processes an instance from the input file."""
    with open(f"instances/{instance}") as file:
        data = file.read().strip().splitlines()

    num_couriers = int(data[0])
    num_items = int(data[1])
    load_sizes = [int(i) for i in data[2].split()]
    item_sizes = [int(i) for i in data[3].split()]
    distances = [[int(j) for j in data[4 + i].split()] for i in range(num_items + 1)]

    return num_couriers, num_items, load_sizes, item_sizes, distances

def extract_solution(model, paths, num_couriers, num_items, depot):
    """Extracts the solution from the Z3 model."""
    solution = []
    all_items = set()
    for i in range(num_couriers):
        route = []
        current = depot
        while True:
            next_node = [k for k in range(num_items+1) if is_true(model[paths[i][current][k]])]
            if not next_node or next_node[0] == depot:
                break
            route.append(next_node[0] + 1)
            all_items.add(next_node[0])
            current = next_node[0]
        solution.append(route)
    
    return solution if len(all_items) == num_items else None

def Max(vec):
    max = vec[0]
    for v in vec[1:]:
        max = If(v > max, v, max)
    return max


def SMT_model(num_couriers, num_items, load_sizes, item_sizes, distances, sb=None, timeout = 300): 
        
    # Define decision variables
    paths = [[[Bool(f"courier_{c}_{j}_{k}") for k in range(num_items+1)] for j in range(num_items+1)] for c in range(num_couriers)]
    order = [Int(f"order{i}") for i in range(num_items)]
    max_dist = Int("max_dist")

    solver = Optimize()
    solver.set_on_model(callback)
    callback.step_counter = 0
    start_time = timer()


    # Constraints on decision variables domains
    for i in range(num_items):
        solver.add(And(order[i] >= 0, order[i] <= num_items-1))


    for i in range(num_couriers):
        for k in range(num_items):
            solver.add(Sum([paths[i][j][k] for j in range(num_items+1)]) == Sum([paths[i][k][j] for j in range(num_items+1)]))

    for k in range(num_items):
        solver.add(Sum([paths[i][j][k] for i in range(num_couriers) for j in range(num_items+1)]) == 1)


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
    for i in range(num_couriers):
        solver.add(Sum([paths[i][j][k] * distances[j][k] for j in range(num_items+1) for k in range(num_items+1)]) <= max_dist)

    # Calculation of lower and upper bounds
    num_nodes = num_items + 1
    depot = num_nodes - 1
    lower_bound = max([distances[depot][j] + distances[j][depot] for j in range(num_nodes - 1)])    
    upper_bound = sum([max(distances[i]) for i in range(num_nodes)])

    solver.add(max_dist >= lower_bound)
    solver.add(max_dist <= upper_bound)


    # Symmetry breaking
    if sb: 
        for i1 in range(num_couriers):
            for i2 in range(num_couriers):
                if i1 < i2 and load_sizes[i1] == load_sizes[i2]:
                    for j in range(num_items):
                        for k in range(num_items):
                            solver.add(Implies(And(paths[i1][num_items][j], paths[i2][num_items][k]), j < k))

    end_time = timer()
    elapsed_time = end_time - start_time
    solver.set("timeout", timeout*1000 - int(elapsed_time * 1000))
    best_sol = None
    # Improved binary search
    while lower_bound < upper_bound and (timer() - start_time) < 300:
        current_target = (lower_bound + upper_bound) // 2
        solver.push()
        solver.add(max_dist <= current_target)
        
        remaining = 300 - (timer() - start_time)
        solver.set("timeout", int(remaining * 1000))
        
        status = solver.check()
        
        if status == sat:
            model = solver.model()
            best_obj = current_target
            upper_bound = current_target

            # Extract complete solution
            best_sol = extract_solution(model, paths, num_couriers, num_items, num_items)
            
            solver.pop()
        elif status == unsat:
            lower_bound = current_target + 1
            solver.pop()
        else:
            break  # Timeout

    # Final verification of the solution
    if best_sol is not None:
        delivered_items = set()
        for route in best_sol:
            delivered_items.update([x-1 for x in route])
        assert len(delivered_items) == num_items, "Missing items in the final solution"

    time = math.floor(timer() - start_time)
    result = {
        "time": time if time <= 300 else 300,
        "optimal": (lower_bound >= upper_bound) and (timer() - start_time) < 300,
        "obj": best_obj if best_sol else None,
        "sol": best_sol if best_sol else None
    }
        
    return result
