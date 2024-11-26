from z3 import *

def get_item(arr, idx):
    # Second and Third If element must be of the same type 
    result = arr[0]
    for i in range(len(arr)):
        result = If(i == idx,arr[i],result)
    return result

def Min(arr):
    minimum = arr[0]
    for i in arr:
        minimum = If(i < minimum,i,minimum)
    return minimum


def Max(arr):
    maximum = arr[0]
    for i in arr:
        maximum = If(maximum < i,i,maximum)
    return maximum


def subcircuit(x, row):
    # taken from fzn_subcircuit.mzn 
    S = range(len(x))  
    u = max(S)

    # Variables 
    order = Array(f"order_{row}", IntSort(),IntSort())
    ins  = [Bool(f'ins_{i}_{row}') for i in S]
    for i in S:
        ins[i] = (x[i] != i +1)
    

    firstin = Int(f'firstin_{row}')
    lastin = Int(f'lastin_{row}')
    empty = Bool(f'empty_{row}')

    constraints = []
    constraints.append(Distinct(x))
    constraints.append(Distinct(order))
    constraints.append(firstin == Min([u+1 + (ins[i])*(i-u-1) for i in S]))
    constraints.append(empty == (firstin > u))

    # If the subcircuit is empty then each node points at itself.
    for i in S:
        constraints.append(Implies(empty, Not(ins[i])))

    constraints.append(Implies(Not(empty),
                               And(
                                    # The firstin node is numbered 1 in the order array
                                    Select(order, firstin) == 1,
                                    # The lastin node is greater than firstin
                                    lastin > firstin,
                                    # The lastin node points at firstin.
                                    get_item(x, lastin) == firstin + 1,
                                    # And both are in
                                    #get_item is okay beacuse ins is an array of booleans
                                    get_item(ins, lastin),
                                    get_item(ins, firstin),
                                    # The successor of each node except where it is firstin is numbered one more than the predecessor.
                                    And([Implies(And(ins[i], x[i] - 1 != firstin), Select(order, x[i] - 1) == Select(order, i) + 1) for i in S]),
                                    # Each node that is not in is numbered after the lastin node.
                                    And([Or(ins[i], Select(order, lastin) < Select(order, i)) for i in S])
                                )))
    return constraints
