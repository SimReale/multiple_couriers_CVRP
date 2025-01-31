from itertools import combinations
from z3 import *
import math
from time import time



# ----- Utils ----- #

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException('Time exceeded!')

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
    with open('instances/'+file_path, 'r') as f:
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

    #upper_bound = sum([max(D[i]) for i in range(n+1)])

    return lower_bound, upper_bound

def Max(vec):
    max = vec[0]
    for v in vec[1:]:
        max = If(v > max, v, max)
    return max



# ----- Naive Pairwise Encodings ----- #

def at_least_one(bool_vars):
    return Or(bool_vars)

def at_most_one(bool_vars):
    return And([Not(And(elems[0], elems[1])) for elems in combinations(bool_vars, 2)])

def exactly_one(bool_vars):
    return And(at_least_one(bool_vars), at_most_one(bool_vars))