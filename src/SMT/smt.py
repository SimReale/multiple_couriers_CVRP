from z3 import *
import os
from utils import * 
import numpy as np

def main():
    #take the instances

    directory = 'src/instances'
    instances = os.listdir(directory)
    instances.sort()
    for instance in instances:
        with open(directory + '/' + instance) as file:
            data = file.read().strip().splitlines()
        m = int(data[0]) #number couriers
        n = int(data[1]) #number of items
        l = [int(i) for i in data[2].split()] #courier capacity
        s = [int(i) for i in data[3].split()] #size items
        distances = []
        #letsgowskyyyyyy
        for i in range(n+1):
            row = [int(j) for j in data[4+i].split()]
            distances.append(row)

        #max_distance = sum([max(row) for row in distances])
        #max_load = max(l)

        #-----variables

        #path
        x = [ [ Int(f"x_{i}_{j}") for j in range(n+1) ] for i in range(m) ]

        #distance couriers
        y = [ Int(f"y_{i}") for i in range(m) ]
        max_y = Int("max_y")

        #load couriers
        load = [ Int(f"l_{i}") for i in range(m) ]

        #-----contraints

        solver = Optimize()
        solver.set("timeout", 5*60*1000)

        for i in range(m):
            # domain contraints
            solver.add([x[i][j] <= n+1  for j in range(n+1)])
            solver.add([x[i][j] >= 1 for j in range(n+1)])
            
            # the load carried by each courier must be lower than the maximum load given in input
            solver.add(sum([If(x[i][j] != j+1, s[j], 0) for j in range(n)]) <= l[i])

            # all couriers left the depot
            solver.add(x[i][n] != n+1)

            # total path cost 
            solver.add(y[i] == sum([get_item(distances[j], x[i][j]-1) for j in range(n+1)]))

            # subcircuit
            solver.add(subcircuit(x[i], i))

        # resources, one per column 
        for j in range(n):
            solver.add(sum([If(x[i][j] == j+1, 1, 0) for i in range(m)]) == m - 1)

        solver.add([max_y >= y[i] for i in range(m)])
        solver.minimize(max_y)
        result = solver.check()
        model = solver.model()

        solution = sorted(
            [(str(i), model[i]) for i in model], key=lambda x: str(x[0][-1])
        )

        path = np.zeros((m ,n+1), int)
        objective = np.inf
        for i in range(len(solution)):
            if solution[i][0][:2] == 'x_':
                path[int(solution[i][0][2])][int(solution[i][0][-1])] = solution[i][1].as_long()
            if solution[i][0] == 'max_y':
                objective = solution[i][1].as_long()
        print(path, '\n', objective, '\n', result)

if __name__ == "__main__":
    main()