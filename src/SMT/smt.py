from z3 import *
import os
from utils import * 


def main():
    #take the instances
    directory = 'src/instances'
    instances = os.listdir(directory)
    instances.sort()
    for instance in instances[:1]:
        with open(directory + '/' + instance) as file:
            data = file.read().strip().splitlines()
        m = int(data[0]) #number couriers
        n = int(data[1]) #number of items
        l = [int(i) for i in data[2].split()] #courier capacity
        s = [int(i) for i in data[3].split()] #size items
        distances = []
        for i in range(n+1):
            row = [int(j) for j in data[4+i].split()]
            distances.append(row)
        num_couriers = int(data[0])
        num_items = int(data[1])


        max_distance = sum([max(row) for row in distances])
        max_load = max(l)

        #-----variables

        #path
        x = [ [ Int(f"x_{i}_{j}") for j in range(n+1) ] for i in range(m) ]
        
        #distance couriers
        y = [ Int(f"y_{i}") for i in range(m) ]
        max_y = Int("max_y")

        
        print(max_y)
        #load couriers
        load = [ Int(f"l_{i}") for i in range(m) ]

        #-----contraints

        solver = Optimize()

        for i in range(m):
            # load constraint 
            solver.add(sum([x[i][j] for j in range(n+1)]) <= l[i])
            # each courier leave the depot 
            solver.add(load[i] > 0)
            # the load carried by each courier must be lower than the maximum load given in input
            solver.add(And(load[i] == sum([If(x[i][j] != j, s[j],0) for j in range(n)]),load[i] <= l[i]))

            # total path cost 
            # solver.add(y[i] == sum([If(x[i][j] != j, get_item(distances[j],[x[i][j]]),0) for j in range(n+1)]))

            # subcircuit
            solver.add(subcircuit(x[i], i))

                
        # resources, one per column 
        for j in range(n):
            solver.add(sum([If(x[i][j] == j, 1, 0) for i in range(m)]) == m - 1)


        solver.add([max_y >= y[i] for i in range(m)])
        solver.minimize(max_y)






if __name__ == "__main__":
    main()