from pymzn import dzn
import os, json
import numpy as np
import re
def to_mzn(instance):
    text = ''
    n = instance["n"]
    for k, v in instance.items():
        #print(v, len(v), '\n')
        if isinstance(v, list):
            v = np.array(v)
            if len(v.shape) == 1:        
                v = '[' + ', '.join([str(x) for x in v]) + ']'
            else:
                formatted_v = '[|'
                for i,row in enumerate(v):
                    formatted_v += ', '.join([str(x) for x in row])
                    if i != n:
                        formatted_v += ', \n \t\t     | '
                formatted_v += ' |]'
                v = formatted_v
        text += f'{k} = {v};\n'

    return text

def parse_dat(text):
    lines = text.split("\n")
    # regex to get a number from a string
    num_regex = r"(\d+)"
    lines = [x for x in lines if x != ""]
    lines = [x.strip() for x in lines]
    m = int(re.findall(num_regex, lines[0])[0])
    n = int(re.findall(num_regex, lines[1])[0])
    l = [int(x) for x in re.findall(num_regex, lines[2])]
    s = [int(x) for x in re.findall(num_regex, lines[3])]

    distances = []
    for i in range(4, 4 + n + 1):
        distances.append([int(x) for x in re.findall(num_regex, lines[i])])

    return {
        "m": m,
        "n": n,
        "l": l,
        "s": s,
        "distances": distances
    }


names = ["m", "n", "l", "s", "distances"]
new_dir = "./dir"
if not os.path.exists(new_dir):
    os.makedirs(new_dir)
for i in range(1, 22):
    if i < 10:
        j = "0"+str(i)
    else: 
        j = str(i)
    file_name = 'inst'+j
    if i != 1:
        os.chdir('../data')
    else:
        os.chdir('./data')
    with open(file_name+'.dat', "r") as instance:
        new_file = parse_dat(instance.read())
        instance = to_mzn(new_file)

    os.chdir('../'+new_dir)
    with open(file_name+".dzn", "w") as f:
        f.write(instance)

'''from minizinc import Instance, Model, Solver

# Load the model from file
nqueens = Model("./nameofthemodel.mzn")
# Find the MiniZinc solver configuration for Gecode
gecode = Solver.lookup("gecode")
#Instance of the model for Gecode
instance = takeaninstance
result = instance.solve()'''