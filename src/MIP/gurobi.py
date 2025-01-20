import gurobipy as gp
from gurobipy import GRB, quicksum
import os

def main():
    #read instances
    directory = 'src/instances'
    instances = os.listdir(directory)
    instances.sort()
    for instance in instances[9:10]:
        print(f'solving {instance}...', end='\n\n')
        with open(directory + '/' + instance) as file:
            data = file.read().strip().splitlines()
        m = int(data[0]) #number COURIERS
        n = int(data[1]) #number of items
        l = [int(i) for i in data[2].split()] #courier capacity
        s = [int(i) for i in data[3].split()] #size items
        distances = []
        for i in V:
            row = [int(j) for j in data[4+i].split()]
            distances.append(row)
        
        #create a new Model
        model = gp.Model()

        #variables
        x = model.addVars(n+1, n+1, m, vtype=GRB.BINARY, name="x") #xijc = 1 iﬀ vehicle c moves from node i to j; 0 otherwise
        y = model.addVars(n+1, m, vtype=GRB.BINARY, name="y") #yic = 1 iﬀ vehicle c visits node i ; 0 otherwise
        u = model.addVars(n+1, m, vtype=GRB.INTEGER, name= 'u') #uic is the cumulated demand serviced by vehicle c when arriving at node i

        max_distance = model.addVar(vtype=GRB.INTEGER, name="max_distance") 
        #load = model.addVars(m, vtype=GRB.INTEGER, name="load")

        #objective
        model.setObjective(max_distance, sense=GRB.MINIMIZE)
        
        #constraints

        for c in COURIERS:
            #minimize total travel cost
            model.addConstr(max_distance >= quicksum(x[i,j,c]*distances[i][j] for i in V for j in V))

        for i in ITEMS:
            #A customer is visited by exactly one vehicle
            model.addConstr(quicksum(y[i,c] for c in COURIERS)==1)
            #every location must be visited exactly once, sum by column
            model.addConstr(quicksum(x[i,j,c] for j in V for c in COURIERS)==1)
            
        for j in ITEMS:
            #every location must be visited exactly once, sum by row
            model.addConstr(quicksum(x[i,j,c] for i in V for c in COURIERS)==1)

        #every courier leave the depot
        model.addConstr(quicksum(y[0,c] for c in COURIERS)==m)

        for c in COURIERS:
            #load carried lower than the capacity of the courier
            model.addConstr(quicksum(y[i,c]*s[i-1] for i in ITEMS)<=l[c-1])

            #cannot move from one position to itself
            model.addConstr(quicksum(x[j,j,c] for j in V)==0)
            
            #every courier must arrive to the depot exactly once
            model.addConstr(quicksum(x[i,0,c] for i in V)==1)
            
            #Path-flow useless since we do not have depot in the last row and column, just in the first one
            #model.addConstr((quicksum(x[0, j, c] for j in ITEMS) - quicksum(x[j, 0, c] for j in ITEMS)) == 1)

        for i in ITEMS:
            for c in COURIERS:
                #Path-flow
                model.addConstr(quicksum(x[i,j,c] for j in V)-quicksum(x[j,i,c] for j in V)==0)
                #Coupling constraint
                model.addConstr(quicksum(x[j,i,c] for j in V)==y[i,c])
        
        #Miller, Tucker and Zemlin constraint
        for c in COURIERS:
            for i in ITEMS:
                for j in ITEMS:
                    if i != j:
                        model.addConstr(u[i, c] - u[j, c] + n * x[i, j, c] <= n - 1)
        
        '''for c in COURIERS:
            for j in V:
                model.addConstr(quicksum(x[i,j,c] for i in V)==quicksum(x[i,j,c] for i in V))'''
        
        '''for i in ITEMS:
            for j in ITEMS:
                if i != j:
                    model.addConstr(u[i,c] - u[j,c] + n * x[i, j, c] <= n - 1)'''
                        



        #time limit
        time_limit = 300
        model.setParam(GRB.Param.TimeLimit, time_limit)

        model.optimize()

        if model.status == GRB.OPTIMAL:
            print("Optimal solution found!")
            print("Optimal Objective Value:", model.objVal)
            '''for V in model.getVars():
                print(V.varName, V.x)'''
if __name__ == "__main__":
    main()