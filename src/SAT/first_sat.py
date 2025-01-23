from sat_utils import *
from time import time

# ----- Instance Reading ----- #
SRC_PATH = 'src/instances/inst02.dat'
m, n, L, S, D = read_instance(SRC_PATH)
print("m:", m)
print("n:", n)
print("L:", L)
print("S:", S)
print("D:", D)

cours = range(m)
packs = range(n)
locs = range(n+1)

# ----- Decision Variables ----- #
# assignments
assignments = [[Bool(f"a_{c}_{p}") for p in packs] for c in cours]

# paths
paths = [[[Bool(f"p_{c}_{s}_{e}") for e in locs] for s in locs] for c in cours]

# MTZ subtour
u = [[[Bool(f"u_{c}_{p}_{k}") for k in packs] for p in packs] for c in cours]

solver = Optimize()
solver.set("timeout", 300000)
#set_option("sat.local_search", True)



# ----- Constraints ----- #
at_most_one = at_most_one_np
exactly_one = exactly_one_np

# each pack must be delivered
for p in packs:
    solver.add(exactly_one([assignments[c][p] for c in cours]))

'''# each courier must deliver at least one pack
for c in cours:
    solver.add(at_least_one([assignments[c][p] for p in packs]))'''

# each courier must start and end in the depot and must take a pack
for c in cours:
    solver.add(exactly_one([paths[c][n][e] for e in locs]))
    solver.add(exactly_one([paths[c][s][n] for s in locs]))
    solver.add(paths[c][n][n] == False)

    # The load carried by each courier is the sum of the sizes of the packages assigned to them.
    solver.add(Sum([If(assignments[c][p], S[p], 0) for p in packs]) <= L[c])

    # channelling constraints
    for p in packs:
        solver.add(assignments[c][p] == And(exactly_one([paths[c][p][e] for e in locs]), exactly_one([paths[c][s][p] for s in locs])))
        solver.add(Implies(assignments[c][p], paths[c][p][p]==False))
        solver.add(Implies(Not(assignments[c][p]), And([paths[c][p][e]==False for e in locs])))

'''# The load carried by each courier is the sum of the sizes of the packages assigned to them.
for c in cours:
    solver.add(Sum([If(assignments[c][p], S[p], 0) for p in packs]) <= L[c])'''

'''# channelling constraints
for c in cours:
    for p in packs:
        solver.add(assignments[c][p] == And(exactly_one([paths[c][p][e] for e in locs]), exactly_one([paths[c][s][p] for s in locs])))
        solver.add(Implies(assignments[c][p], paths[c][p][p]==False))
        solver.add(Implies(Not(assignments[c][p]), And([paths[c][p][e]==False for e in locs])))'''

# SUBTOUR
# Constraining assignment of truth value of u decision variable
for c in cours:
    # u for first pack = 1
    for p in packs:
        solver.add(Implies(paths[c][n][p], u[c][p][0]==True))

    for p1 in packs:
        for p2 in packs:
            if p1 == p2:
                continue

            for k in packs:
                solver.add(Implies(And(paths[c][p1][p2], u[c][p1][k]), exactly_one([u[c][p2][i] for i in range(k+1, n)])))

## Exatcly one true value for each u_p1
for c in cours:
    for p1 in packs:
        solver.add(exactly_one(u[c][p1]))

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



# ----- Objective Function ----- #
'''max_distance = binary_to_integer(distances[0])
for c in cours[1:]:
    max_distance = If(binary_to_integer(distances[c]) > max_distance,
                      binary_to_integer(distances[c]),
                      max_distance)'''

distances = [Sum([If(paths[c][s][e], D[s][e], 0) for s in locs for e in locs if s != e]) for c in cours]
max_distance = distances[0]
for dist in distances[1:]:
    max_distance = If(dist > max_distance, dist, max_distance)
solver.minimize(max_distance)



# ----- Solve the Problem ----- #
start_time = time()
status = solver.check()
if status != unsat:
    model = solver.model()
    print("\nSolution found:")
    
    # Retrieve assignments
    print("\nAssignments:")
    for c in cours:
        assigned_packs = [p for p in packs if model.evaluate(assignments[c][p])]
        print(f"Courier {c}: {assigned_packs}")
    
    # Retrieve paths
    print("\nPaths:")
    for c in cours:
        path = [(s, e) for s in locs for e in locs if s != e and model.evaluate(paths[c][s][e])]
        print(f"Courier {c}: {path}")
    
    # Retrieve distances
    '''print("\nDistances:")
    for c in cours:
        print(f"Courier {c}: {distances[c]}")'''
    
    # Retrieve the maximum distance
    print("\nMaximum Distance Traveled:")
    print(model.evaluate(max_distance))
else:
    print("No solution found.")
print(f"Execution Time: {time() - start_time:.2f} seconds")