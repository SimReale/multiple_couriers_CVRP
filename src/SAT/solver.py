from SAT.sat_utils import *
from SAT.path_mtz import MTZ_model
import json

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
        res = MTZ_model(m, n, L, S, D, timeout)
        results["MTZ_model"] = res

        result_filename = f"results/SAT/{inst.removesuffix('.dat')}.json"
        with open(result_filename, "w") as json_file:
            json.dump(results, json_file, indent=4)

if __name__ == "__main__":
    solve()