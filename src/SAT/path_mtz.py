from SAT.sat_utils import *

'''SRC_PATH = 'src/instances/inst05.dat'
m, n, L, S, D = read_instance(SRC_PATH)
print("m:", m)
print("n:", n)
print("L:", L)
print("S:", S)
print("D:", D)'''



def MTZ_model(m, n, L, S, D):

    cours = range(m)
    packs = range(n)
    order = range(n)
    locs = range(n+1)

    # ----- DECISION VARIABLES ----- #

    # assignments
    assignments = [[Bool(f"a_{c}_{p}") for p in packs] for c in cours]

    # paths
    paths = [[[Bool(f"p_{c}_{s}_{e}") for e in locs] for s in locs] for c in cours]

    # MTZ subtour
    u = [[[Bool(f"u_{c}_{p}_{o}") for o in order] for p in packs] for c in cours]

    # Solver
    solver = Solver()
    start_time = time()



    # ----- CONSTRAINTS ----- #

    at_most_one = at_most_one_np
    exactly_one = exactly_one_np

    '''# each pack must be delivered
    for p in packs:
        solver.add(exactly_one([assignments[c][p] for c in cours]))

    for c in cours:
        # each courier must start and end in the depot and must take a pack
        solver.add(exactly_one([paths[c][n][e] for e in locs]))
        solver.add(exactly_one([paths[c][s][n] for s in locs]))

        # each courier must deliver at least one pack
        solver.add(Not(paths[c][-1][-1]))

        # The load carried by each courier is lower than its capacity
        solver.add(Sum([If(exactly_one(paths[c][p]), S[p], 0) for p in packs]) <= L[c])

        # channelling constraints
        for p in packs:
            solver.add(Implies(assignments[c][p], And(exactly_one([paths[c][p][e] for e in locs]), exactly_one([paths[c][s][p] for s in locs]))))
            solver.add(Implies(assignments[c][p], Not(paths[c][p][p])))
            solver.add(Implies(Not(assignments[c][p]), And([And(Not(paths[c][p][e]), Not(paths[c][e][p])) for e in locs])))

            # u assignment for the first pack
            solver.add(Implies(paths[c][n][p], u[c][p][0]))
            # Exatcly one true value for each u_p1
            solver.add(exactly_one(u[c][p]))

            for p_dest in packs:
                if p != p_dest:
                    for o in packs:
                        # Constraining assignment of truth value of u decision variable
                        solver.add(Implies(And(paths[c][p][p_dest], u[c][p][o]), exactly_one([u[c][p_dest][i] for i in range(o+1, n)])))

                        # MTZ formulation constraint
                        for o_dest in order:
                            solver.add(Implies(And(u[c][p][o], u[c][p_dest][o_dest]), o - o_dest + 1 <= (n-1) * (1-If(paths[c][p][p_dest], 1, 0))))'''
    
    ##########
    # each pack must be delivered
    for p in packs:
        solver.add(exactly_one([assignments[c][p] for c in cours], "assignment"))

    for c in cours:
        # each courier must start and end in the depot and must take a pack
        solver.add(exactly_one([paths[c][n][e] for e in locs], "depot_start"))
        solver.add(exactly_one([paths[c][s][n] for s in locs], "depot_end"))

        # each courier must deliver at least one pack
        solver.add(Not(paths[c][n][n]))

        # The load carried by each courier is lower than its capacity
        solver.add(Sum([If(assignments[c][p], S[p], 0) for p in packs]) <= L[c])

        # channelling constraints
        for p in packs:
            solver.add(Implies(assignments[c][p], And(exactly_one([paths[c][p][e] for e in locs], "pack_start"), exactly_one([paths[c][s][p] for s in locs], "pack_end"))))
            solver.add(Implies(assignments[c][p], Not(paths[c][p][p])))
            solver.add(Implies(Not(assignments[c][p]), And([And(Not(paths[c][p][e]), Not(paths[c][e][p])) for e in locs])))
    
            '''for e in packs:
                solver.add(Implies(paths[c][p][e], And(assignments[c][p], assignments[c][e])))'''

    # SUBTOUR
    # Constraining assignment of truth value of u decision variable
    for c in cours:
        # u for first pack = 1
        for p in packs:
            solver.add(Implies(paths[c][n][p], u[c][p][0]))

        for p1 in packs:
            for p2 in packs:
                if p1 == p2:
                    continue

                for k in packs:
                    solver.add(Implies(And(paths[c][p1][p2], u[c][p1][k]), exactly_one([u[c][p2][i] for i in range(k+1, n)], "order")))

    ## Exatcly one true value for each u_p1
    for c in cours:
        for p1 in packs:
            solver.add(exactly_one(u[c][p1], "pack_deliver"))

    # Applying MTZ formulation constraint
    # u_i - u_j + 1 <= (n - 1) * (1 - paths[c, i, j])
    for c in cours:
        for p1 in packs: # i
            for p2 in packs: #j
                if p1 == p2:
                    continue

                for k1 in packs:
                    for k2 in packs:
                        solver.add(Implies(And(u[c][p1][k1], u[c][p2][k2]), k1 - k2 + 1 <= (n-1) * (1-If(paths[c][p1][p2], 1, 0))))



    # ----- OBJECTIVE FUNCTION ----- #

    lower_bound, upper_bound = compute_bounds(m, n, D)
    max_distance = [Bool(f"d_{b}") for b in range(n_bits(upper_bound))]
    solver.add(binary_to_integer(max_distance) == Max([Sum([If(paths[c][s][e], D[s][e], 0) for s in locs for e in locs if s != e]) for c in cours]))

    solver.add(binary_to_integer(max_distance) >= lower_bound)



    # ----- PROBLEM SOLVING ----- #

    res = {}
    elapsed_time = time() - start_time
    solve_time = elapsed_time
    curr_objective = upper_bound
    #set_param('sat.restart', 'luby')
    #set_param('sat.local_search', True)
    #set_param('sat.local_search_threads', 1)
    #set_param('sat.prob_search', True)

    

    while elapsed_time < 300:
        solver.set("timeout", math.floor(300000 - solve_time*1000))
        solver.push()

        # binary search
        new_upper_bound = (lower_bound + curr_objective)//4
        solver.add(binary_to_integer(max_distance) < new_upper_bound)

        status = solver.check()
        solve_time = time() - start_time

        if status == unsat or curr_objective == lower_bound:
            res["time"] = math.floor(solve_time)
            res["optimal"] = True
            break

        if status == unknown or (time()-start_time) >= 300:
            res["time"] = math.floor(solve_time) if math.floor(solve_time) == 300 else 300
            break
        
        model = solver.model()
        solver.pop()

        dists = []
        result_paths = []
        for c in cours:
            c_path = [p+1 for p in packs if model.evaluate(paths[c][-1][p])]
            while c_path[-1] != n+1:
                c_path.extend([l+1 for l in locs if model.evaluate(paths[c][c_path[-1]-1][l])])
            c_path.pop()
            result_paths.append(c_path)

            c_dist = D[-1][c_path[0]-1]
            for i in range(len(c_path)-1):
                c_dist += D[c_path[i]-1][c_path[i+1]-1]
            c_dist += D[c_path[-1]-1][-1]
            dists.append(c_dist)
        curr_objective = max(dists)



        res["time"] = math.floor(solve_time)
        res["optimal"] = False
        res["obj"] = curr_objective
        res["sol"] = result_paths

    print("\nNew instance:")
    print(res)
    
    return res

#fr = MTZ_model(m, n, L, S, D)