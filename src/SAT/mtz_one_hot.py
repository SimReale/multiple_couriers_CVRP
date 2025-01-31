from SAT.sat_utils import *
import signal
import gc


def MTZ_model(m, n, L, S, D, timeout, symm=False):

    # Results initialisation
    res = {
        "time": timeout,
        "optimal": False,
        "obj": None,
        "sol": None
    }

    # Timeout initialization
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    start_time = time()

    try:
        cours = range(m)
        packs = range(n)
        locs = range(n+1)

        # ----- DECISION VARIABLES AND SOLVER ----- #

        # paths
        paths = [[[Bool(f"p_{c}_{s}_{e}") for e in locs] for s in locs] for c in cours]

        # ordering variable
        u = [[Bool(f"u_{p}_{o}") for o in packs] for p in packs]

        # Solver
        solver = Solver()



        # ----- AUXILIARY VARIABLES ----- #

        # assignments
        assignments = [[Bool(f"a_{c}_{p}") for p in packs] for c in cours]



        # ----- CONSTRAINTS ----- #
        
        # each pack must be delivered
        for p in packs:
            solver.add(exactly_one([assignments[c][p] for c in cours]))

        for c in cours:
            # each courier must start and end in the depot and must take a pack
            solver.add(exactly_one([paths[c][-1][e] for e in locs]))
            solver.add(exactly_one([paths[c][s][-1] for s in locs]))

            # each courier must deliver at least one pack
            solver.add(Not(paths[c][n][n]))

            # The load carried by each courier is lower than its capacity
            solver.add(PbLe([(assignments[c][p], S[p]) for p in packs], L[c]))

            # channelling constraints
            for p in packs:
                tstp_1 = time() - start_time

                solver.add(Implies(assignments[c][p], And(exactly_one([paths[c][p][e] for e in locs]), exactly_one([paths[c][s][p] for s in locs]))))
                solver.add(Implies(assignments[c][p], Not(paths[c][p][p])))
                solver.add(Implies(Not(assignments[c][p]), And([And(Not(paths[c][p][e]), Not(paths[c][e][p])) for e in locs])))

                tstp_2 = time() - start_time
                if (tstp_2 - tstp_1) * (n-p-1) > 300 - tstp_2:
                    raise TimeoutException

        # assignment of the ordering variables for u
        for p1 in packs:
            # first packs delivered
            solver.add(Implies(paths[c][n][p1], u[p1][0]))

            # each pack is delivered only once
            solver.add(exactly_one(u[p1]))

            # following packs
            for p2 in packs:
                if p1 != p2:
                    for o in packs[:-1]:
                        solver.add(Implies(And(paths[c][p1][p2], u[p1][o]), u[p2][o+1]))

        # MTZ formulation for subtour elimination
        for p1 in packs:
            for p2 in packs:
                if p1 != p2:
                    for o1 in packs:
                        for o2 in packs:
                            solver.add(Implies(And(u[p1][o1], u[p2][o2]), 
                                               o1 - o2 + 1 <= (n-1) * (1-If(at_least_one([paths[c][p1][p2] for c in cours]), 1, 0))))
        


        # ----- SYMMETRY BREAKING CONSTRAINTS ----- #

        if symm == True:
            for p1 in packs:
                for p2 in packs:

                    # lexicographic ordering on the paths
                    solver.add(And([Implies(And(paths[c][-1][p1], paths[c][p2][-1]), p1 <= p2) for c in cours]))

                    # lexicographic ordering on the loads
                    if p1 != p2:
                        solver.add([Implies(And(S[p1] == S[p2], Sum([If(assignments[c1][p], S[p], 0) for p in packs]) == Sum([If(assignments[c2][p], S[p], 0) for p in packs])), 
                                            And([assignments[c1][p1], assignments[c2][p2], c1 < c2])) for c1 in cours for c2 in cours if c1 != c2])
                        
                        #solver.add([Implies(And([assignments[c1][p1], assignments[c2][p2], L[c1] == L[c2], S[p1] == S[p2]]), c1 < c2) for c1 in cours for c2 in cours])



        # ----- OBJECTIVE FUNCTION ----- #

        lower_bound, upper_bound = compute_bounds(m, n, D)
        max_distance = [Bool(f"d_{b}") for b in range(n_bits(upper_bound))]
        solver.add(binary_to_integer(max_distance) == Max([Sum([If(paths[c][s][e], D[s][e], 0) for s in locs for e in locs if s != e]) for c in cours]))

        solver.add(binary_to_integer(max_distance) >= lower_bound)
    
    except ctypes.ArgumentError:

        # Reset the alarm
        signal.alarm(0)

    except TimeoutException:

        # Reset the alarm
        signal.alarm(0)

    else:
        # Reset the alarm
        signal.alarm(0)



        # ----- PROBLEM SOLVING ----- #

        elapsed_time = time() - start_time
        solve_time = elapsed_time
        curr_objective = upper_bound

        

        while elapsed_time < timeout:

            solver.set("timeout", math.floor((timeout - solve_time)*1000))
            solver.push()

            # Adaptive Binary Search
            '''if curr_objective == upper_bound:
                new_upper_bound = upper_bound'''
            if curr_objective <= 2*lower_bound:
                new_upper_bound = curr_objective
            else:
                new_upper_bound = (lower_bound + curr_objective)//2 + 1
            solver.add(binary_to_integer(max_distance) < new_upper_bound)

            status = solver.check()
            solve_time = time() - start_time

            if status == unsat or curr_objective == lower_bound:
                res["time"] = math.floor(solve_time)
                res["optimal"] = True
                break

            if status == unknown or (time()-start_time) >= timeout:
                res["time"] = math.floor(solve_time) if math.floor(solve_time) == timeout else timeout
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

    solver.reset()
    del solver
    gc.collect()

    return res