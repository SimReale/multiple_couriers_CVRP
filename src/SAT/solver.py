from SAT.sat_utils import *
from SAT.mtz_one_hot import MTZ_model
import json

def solve(instances, model_name= None, solver_name= None, timeout = 300):

    for instance_number, inst in enumerate(instances, 1):
        
        results = {}
        m, n, L, S, D = read_instance(inst)
        res = MTZ_model(m, n, L, S, D, timeout)
        results["mtz_base"] = res

        res_sb = MTZ_model(m, n, L, S, D, timeout, symm=True)
        results["mtz_symm"] = res_sb

        result_filename = f"results/SAT/{instance_number}.json"
        with open(result_filename, "w") as json_file:
            json.dump(results, json_file, indent=4)

if __name__ == "__main__":
    solve()