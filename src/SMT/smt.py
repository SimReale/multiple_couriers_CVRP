from z3 import *
import os

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

        
        max_distance = sum([max(row) for row in distances])
        max_load = max(l)

        #-----variables

        #path
        x = [ [ Int("x_%s_%s" % (i+1, j+1)) for j in range(n+1) ] 
        for i in range(m) ]
        
        #distance couriers
        y = [ Int("y_%s" % (i+1)) for i in range(m) ]
        max_y = max(y)
        print(max_y)
        #load couriers
        load = [ Int("l_%s" % (i+1)) for i in range(m) ]

        #-----contraints

        solver = Optimize()

        for i in range(1, m+1):
            solver.add(sum([x[i, j] for j in range(n+1)]) <= l[i])

        










if __name__ == "__main__":
    main()