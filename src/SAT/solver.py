from SAT.sat_utils import *
from SAT.mtz_one_hot import MTZ_model
import json
import re

def solve(instances, solver_name= None, model_name= None, timeout = 300):

    if model_name:
        models = model_name
    else:
        models = ['base','symm']

    for inst in instances:

        results = {}

        for model in models:

            m, n, L, S, D = read_instance(inst)
            if model == "symm":
                res = MTZ_model(m, n, L, S, D, timeout, symm=True)
            else:
                res = MTZ_model(m, n, L, S, D, timeout)
            results[model] = res

            instance_number = re.search(r'\d+', inst)
            result_filename = f"res/SAT/{int(instance_number.group())}.json"
            with open(result_filename, "w") as json_file:
                json.dump(results, json_file, indent=4)

if __name__ == "__main__":
    solve()