#from SAT.sat_utils import *
from sat_utils import *

SRC_PATH = 'src/instances/inst07.dat'
m, n, L, S, D = read_instance(SRC_PATH)
print("m:", m)
print("n:", n)
print("L:", L)
print("S:", S)
print("D:", D)

def MTZ_model(m, n, L, S, D):

    cours = range(m)
    packs = range(n)
    order = range(n)
    locs = range(n+1)

    # ----- DECISION VARIABLES ----- #

    # path assignments
    paths = [[[Bool(f"u_{c}_{p}_{o}") for o in order] for p in packs] for c in cours]

    # Solver
    solver = Solver()
    start_time = time()



    # ----- CONSTRAINTS ----- #

    at_most_one = at_most_one_np
    exactly_one = exactly_one_np

    for p in packs:
        # each pack must be delivered
        solver.add(exactly_one([paths[c][p][o] for c in cours for o in order]))

        # enforce pack assignment (if a pack is assigned to one courier then all the paths values for that pack of the other couriers are false)
        #solver.add(And([Implies(paths[]) ])
    
    # each courier must take at least one pack and if one pack is delivered in position k, then
    # at most one pack must be delivered in position k+1
    for c in cours:
        solver.add(exactly_one([paths[c][p][0] for p in packs]))

        '''for o in order[:-1]:
            solver.add(Implies(exactly_one([paths[c][p][o] for p in packs]), at_most_one([paths[c][p][o+1] for p in packs])))
            #solver.add(Implies(And([Not(paths[c][p][o]) for p in packs]), And([Not(paths[c][p][o+1]) for p in packs])))'''

        '''for p in packs:
            for o in order[:-1]:
                solver.add(Implies(paths[c][p][o], at_most_one([paths[c][pk][o+1] for pk in packs])))'''

        # The load carried by each courier is lower than its capacity
        solver.add(Sum([If(exactly_one(paths[c][p]), S[p], 0) for p in packs]) <= L[c])

        # Every courier can deliver at most one pack for each order
        for o in order[1:]:
            #solver.add(at_most_one([paths[c][p][o] for p in packs]))
            solver.add(Implies(at_least_one([paths[c][p][o] for p in packs]), at_least_one([paths[c][p][o-1] for p in packs])))



    # ----- OBJECTIVE FUNCTION ----- #

    lower_bound, upper_bound = compute_bounds(m, n, D)
    distances = []

    for c in cours:
        last = 0
        for p in packs:
            curr_sum = If(paths[c][p][0], D[-1][p], 0)
            if p == If(paths[c][p][0], p, 0):
                last = p
        for o in order:
            curr_sum += If(at_least_one([paths[c][p][o] for p in packs]),
                        sum([If(paths[c][p][o], D[last][p], 0) for p in packs]), 0)
            if p == If(paths[c][p][o], p, 0):
                last = p
        curr_sum += D[last][-1]
        distances.append(curr_sum)
    
    

    max_distance = Max(distances)

    solver.add(max_distance >= lower_bound)



    # ----- PROBLEM SOLVING ----- #

    res = {}
    elapsed_time = time() - start_time
    solve_time = elapsed_time
    curr_objective = upper_bound + 1
    

    while elapsed_time < 300:
        solver.set("timeout", math.floor(300000 - solve_time*1000))
        solver.push()
        solver.add(max_distance < Min([curr_objective, upper_bound]))
        status = solver.check()
        solve_time = time() - start_time

        if status == unsat or curr_objective == lower_bound:
            res["time"] = math.floor(solve_time)
            res["optimal"] = True
            break

        if status == unknown or (time()-start_time) >= 300:
            res["time"] = 300 #math.floor(solve_time)
            break
        
        model = solver.model()
        curr_objective = model.evaluate(max_distance)
        solver.pop()

        dists = []
        result_paths = []
        for c in cours:
            c_path = []
            for o in order:
                c_path.extend([p+1 for p in packs if model.evaluate(paths[c][p][o])])
            result_paths.append(c_path)

            c_dist = D[-1][c_path[0]-1]
            for i in range(len(c_path)-1):
                c_dist += D[c_path[i]-1][c_path[i+1]-1]
            c_dist += D[c_path[-1]-1][-1]
            dists.append(c_dist)
        objective = max(dists)


        
        res["time"] = math.floor(solve_time)
        res["optimal"] = False
        res["obj"] = objective
        res["sol"] = result_paths
    
    print("\nNew instance:")
    print(res)

    return res

fr = MTZ_model(m, n, L, S, D)