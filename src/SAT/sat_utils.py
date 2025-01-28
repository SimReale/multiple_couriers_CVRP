from itertools import combinations
from z3 import *
import math
from time import time


# ----- Utils ----- #

def n_bits(x):
    return math.ceil(math.log2(x))

def integer_to_binary(num, length = None):
    num_bin = bin(num).split("b")[-1]
    if length:
        return "0"*(length - len(num_bin)) + num_bin
    return num_bin

def binary_to_integer(binary_vector):
    n = len(binary_vector)
    integer_expr = 0
    for i in range(n):
        integer_expr += If(binary_vector[i], 2**i, 0)
    return integer_expr

def read_instance(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        m = int(lines[0])
        n = int(lines[1])
        l = list(map(int, lines[2].split()))
        S = list(map(int, lines[3].split()))
        D = []
        for line in lines[4:]:
            D.append(list(map(int, line.split())))
        return m, n, l, S, D

def compute_bounds(m, n, D):
    """
    m = couriers
    n = packs
    D = distance matrix in input
    """
    lower_bound = max([D[-1][p] + D[p][-1] for p in range(n)])
    upper_bound = max([D[-1][indices[0]] + sum([D[indices[i]][indices[i+1]] for i in range(n-m)]) + D[indices[n-m]][-1] for indices in combinations(range(n), n-m+1)])
    return lower_bound, upper_bound

def Max(vec):
    max = vec[0]
    for v in vec[1:]:
        max = If(v > max, v, max)
    return max

def Min(vec):
    min = vec[0]
    for v in vec[1:]:
        min = If(v < min, v, min)
    return min



# ----- Encodings ----- #

def at_least_one(bool_vars):
    return Or(bool_vars)

# Naive Pairwise
def at_most_one_np(bool_vars, name = ""):
    return And([Not(And(elems[0], elems[1])) for elems in combinations(bool_vars, 2)])

def exactly_one_np(bool_vars, name = ""):
    return And(at_least_one(bool_vars), at_most_one_np(bool_vars, name))


# Sequential
def at_most_one_seq(bool_vars, name=""):
    # variables and constraint list declaration
    constraints = []
    n = len(bool_vars)
    if n == 1:
        return And(bool_vars)
    elif n == 0:
        return True
    s = [Bool(f"s_{name}_{i}") for i in range(n-1)]
    

    # constraints definintion
    constraints.append(Or(Not(bool_vars[0]), s[0]))
    #constraints.append(Implies(bool_vars[0], s[0]))
    constraints.append(Or(Not(bool_vars[-1]), Not(s[-1])))
    #constraints.append(Implies(s[n-2], Not(bool_vars[n-1])))
    for i in range(1, n-1):
        '''constraints.append(Implies(Or(bool_vars[i], s[i-1]), s[i]))
        constraints.append(Implies(s[i-1], Not(bool_vars[i])))'''
        constraints.append(Or(Not(bool_vars[i]), s[i]))
        constraints.append(Or(Not(s[i-1]), s[i]))
        constraints.append(Or(Not(s[i-1]), Not(bool_vars[i])))
    return And(constraints)

def exactly_one_seq(bool_vars, name=""):
    return And(at_most_one_seq(bool_vars, name), at_least_one(bool_vars))



# Bitwise
'''def at_most_one_bw(bool_vars, name=""):
    constraints = []
    n = len(bool_vars)
    m = math.ceil(math.log2(n))
    r = [Bool(f"r_{name}_{i}") for i in range(m)]
    binary_encodings = [integer_to_binary(i, m) for i in range(n)]

    for i in range(n):
        for j in range(m):
            if binary_encodings[i][j] == "1":
                constraints.append(Or(Not(bool_vars[i]), r[j]))
            else:
                constraints.append(Or(Not(bool_vars[i]), Not(r[j])))
    return And(constraints)'''

def at_most_one_bw(bool_vars, name=""):
    constraints = []
    n = len(bool_vars)
    if n == 1:
        return And(bool_vars)
    elif n == 0:
        return True
    
    m = math.ceil(math.log2(n))
    r = [Bool(f"r_{name}_{i}") for i in range(m)]
    binaries = [integer_to_binary(i, m) for i in range(n)]
    for i in range(n):
        for j in range(m):
            phi = Not(r[j])
            if binaries[i][j] == "1":
                phi = r[j]
            constraints.append(Or(Not(bool_vars[i]), phi))        
    return And(constraints)

def exactly_one_bw(bool_vars, name=""):
    return And(at_most_one_bw(bool_vars, name), at_least_one(bool_vars))


# Heule
def at_most_one_he(bool_vars, name=""):
    if len(bool_vars) <= 4:
        return And(at_most_one_np(bool_vars))
    y = Bool(f"y_{name}")
    return And(And(at_most_one_np(bool_vars[:3] + [y])), And(at_most_one_he(bool_vars[3:] + [Not(y)], name + "_")))

def exactly_one_he(bool_vars, name=""):
    return And(at_least_one(bool_vars), at_most_one_he(bool_vars, name))