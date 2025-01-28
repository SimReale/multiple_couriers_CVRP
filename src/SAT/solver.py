from SAT.sat_utils import *
from SAT.path_mtz import MTZ_model
import os
import json

def solve():

    inst_dir = "instances"
    instances = os.listdir(inst_dir)
    instances.sort()
    INST_PATHS = [f"{inst_dir}/{i}" for i in instances]

    for i in range(6, len(INST_PATHS[:10])):
        results = {}
        m, n, L, S, D = read_instance(INST_PATHS[i])
        res = MTZ_model(m, n, L, S, D)
        results["MTZ_model"] = res

        result_filename = f"../results/SAT/{instances[i].removesuffix('.dat')}.json"
        with open(result_filename, "w") as json_file:
            json.dump(results, json_file, indent=4)

if __name__ == "__main__":
    solve()