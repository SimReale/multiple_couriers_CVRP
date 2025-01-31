from SAT.sat_utils import *
from SAT.mtz_one_hot import MTZ_model
import json
import re

def solve(instances, model_name= None, solver_name= None, timeout = 300):
    
    #abilitate whether you have multiple models
    # if model_name:
    #     models = [model_name]
    # else:
    #     models = os.listdir('SAT/models')

    for inst in instances:
        #for model in models:
        results = {}
        m, n, L, S, D = read_instance(inst)
        res = MTZ_model(m, n, L, S, D, timeout, symm=True)
        results["MTZ_model"] = res

        instance_number = re.search(r'\d+', inst)
        result_filename = f"results/SAT/{instance_number.group()}.json"
        with open(result_filename, "w") as json_file:
            json.dump(results, json_file, indent=4)

if __name__ == "__main__":
    solve()