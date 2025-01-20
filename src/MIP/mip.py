import gurobipy as gp
from gurobipy import GRB, quicksum
import os

def main():
    #read instances
    directory = 'src/instances'
    instances = os.listdir(directory)
    instances.sort()
    for instance in instances[0:1]:
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

    max_dist = sum([max([dist for dist in row]) for row in distances])
    max_load = max(l)
    
    max_load = max(l)
    #create a new Model
    model = gp.Model()

    #variables
    x = model.addVars(m, n+1, vtype=GRB.INTEGER, name="x")
    x_aux = model.addVars(m, n+1, n+1, vtype=GRB.INTEGER, name="x_aux")
    y = model.addVars(m, lb= 1, ub= max_dist, vtype=GRB.INTEGER, name="y")
    max_distance = model.addVar(lb= 1, ub= max_dist, vtype=GRB.INTEGER, name="max_dist")
    load = model.addVars(m, lb=1, ub= max_load, vtype=GRB.INTEGER, name="load")

    #objective
    model.setObjective(max_distance, sense=GRB.MINIMIZE)
    
    #constraints
    for c in range(m):
        model.addConstr(quicksum(x_aux[c,i,j]*distances[i][j] for i in range(n+1) for j in range(n+1)) <= max_distance)
        
        #the depot column must be different form itself
        model.addConstr(x[c, n] <= n)

        #the load carried is given by the sum of the items size carried 
        model.addConstr(load[c] == quicksum([x_aux[c, i, j]*s[i] for i in range(n) for j in range(n)]))

        #the load carried lower wrt the capacity
        model.addConstr(load[c]<=l[c])

        for i in range(n+1):
            model.addConstr((x[c, i] <= i) >> (x_aux[c, i, 3] == 1))
            model.addConstr((x[c, i] >= i+2) >> (x_aux[c, i, x[c, i]] == 1))



    #time limit
    time_limit = 10
    model.setParam(GRB.Param.TimeLimit, time_limit)

    model.optimize()
if __name__ == "__main__":
    main()