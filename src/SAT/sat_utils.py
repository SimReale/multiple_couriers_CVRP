from itertools import combinations
from z3 import *
import math


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



# ----- Encodings ----- #
def at_least_one(bool_vars):
    return Or(bool_vars)


# Naive Pairwise
def at_most_one_np(bool_vars, name = ""):
    return And([Not(And(elems[0], elems[1])) for elems in combinations(bool_vars, 2)])

def exactly_one_np(bool_vars, name = ""):
    return And(at_least_one(bool_vars), at_most_one_np(bool_vars, name))


# Sequential
def at_most_one_seq(x, name=""):
    n = len(x)
    if n == 1:
        return True
    s = [Bool(f"s_{i}_{name}") for i in range(n-1)]     # s[i] modeled as: s[i] is true iff the sum up to index i is 1

    clauses = []
    clauses.append(Or(Not(x[0]), s[0]))                 # x[0] -> s[0]
    for i in range(1, n-1):
        clauses.append(Or(Not(x[i]), s[i]))             # these two clauses model (x[i] v s[i-1]) -> s[i]
        clauses.append(Or(Not(s[i-1]), s[i]))
        clauses.append(Or(Not(s[i-1]), Not(x[i])))      # this one models s[i-1] -> not x[i]
    clauses.append(Or(Not(s[-1]), Not(x[-1])))          # s[n-2] -> not x[n-1]
    return And(clauses)

def exactly_one_seq(bool_vars, name=""):
    return And(at_least_one(bool_vars), at_most_one_seq(bool_vars, name))

'''def at_most_one_seq(bool_vars, name=""):
    # variables and constraint list declaration
    constraints = []
    n = len(bool_vars)
    s = [Bool(f"s_{name}_{i}") for i in range(n-1)]

    # constraints definintion
    constraints.append(Or(Not(bool_vars[0]), s[0]))
    constraints.append(Or(Not(bool_vars[-1]), Not(s[-2])))
    for i in range(1, n-1):
        constraints.append(And([Or(Not(bool_vars[i]), s[i]),  Or(Not(s[i-1]), s[i]), Or(Not(s[i-1]), Not(bool_vars[i]))]))
    return And(constraints)

def exactly_one_seq(bool_vars, name=""):
    return And(at_most_one_seq(bool_vars, name), at_least_one(bool_vars))'''



# Bitwise
def at_most_one_bw(bool_vars, name=""):
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
    return And(constraints)

def exactly_one_bw(bool_vars, name=""):
    return And(at_most_one_bw(bool_vars, name), at_least_one(bool_vars))


# Heule
def at_most_one_he(bool_vars, name=""):
    if len(bool_vars) <= 4:
        return at_most_one_np(bool_vars)
    y = Bool(f"y_{name}")
    return And(at_most_one_np(bool_vars[:3] + [y]), at_most_one_he([Not(y)] + bool_vars[3:], name + "_"))

def exactly_one_he(bool_vars, name=""):
    return And(at_least_one(bool_vars), at_most_one_he(bool_vars, name))