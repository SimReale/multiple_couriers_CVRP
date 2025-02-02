import os
import re
import subprocess
import logging
import json
from time import sleep
from timeit import default_timer as timer
from SMT.loggin_config import setup_logger
from SMT.extract_solution import *
from SMT.smt_lib_core import * 
import math

logger = logging.getLogger(__name__)


def optimize_max_dist(solver, smt_file_path, output_dir, timeout):
    start_time = timer()
    with open(smt_file_path, 'r') as f:
        original_content = f.read()

    try:
        initial_lower, initial_upper = extract_initial_bounds(original_content)
    except ValueError as e:
        logger.error(f"Error in file {smt_file_path}: {e}")
        return None

    # Remove all existing constraints on max_dist
    base_lines = []
    constraint_pattern = re.compile(r'^\s*\(assert\s+\(([<>]=)\s+max_dist\s+\d+\)\)\s*$')
    for line in original_content.split('\n'):
        stripped = line.strip()
        if not constraint_pattern.search(stripped):
            base_lines.append(line)

    # Find the position to insert the new constraints
    insert_pos = None
    for i, line in enumerate(base_lines):
        if line.strip().startswith(('(check-sat)', '(get-value')):
            insert_pos = i
            break

    best_solution = None
    lower = initial_lower
    upper = initial_upper
    elapsed_time = timer() - start_time
    remaining_time = timeout - elapsed_time

    while lower <= upper and remaining_time > 0:
        current_mid = (lower + upper) // 2
        print(f"Testing range: {lower} <= max_dist <= {current_mid}")

        # Build the content with the updated constraints
        temp_lines = base_lines.copy()
        
        # Add the new dynamic constraints
        new_constraints = [
            f'(assert (>= max_dist {lower}))',
            f'(assert (<= max_dist {current_mid}))\n'
        ]
        
        if insert_pos is not None:
            for constraint in reversed(new_constraints):
                temp_lines.insert(insert_pos, constraint)
        else:
            temp_lines.extend(new_constraints)

        temp_content = '\n'.join(temp_lines)
        
        temp_file = os.path.join(output_dir, f"temp_{lower}_{current_mid}.smt2")
        with open(temp_file, 'w') as f:
            f.write(temp_content)

        solution = solve_smt_file(solver, temp_file, remaining_time)
        actual_time_taken = solution['time']
        remaining_time -= actual_time_taken
        os.remove(temp_file)
        time  = timeout - remaining_time

        if solution and solution['status'] == 'sat':
            solution_data = parse_output(solution['stdout'], math.floor(time))          
            current_dist = solution_data["obj"]
            
            if current_dist:
                # Update the upper bound to the found value -1
                upper = current_dist - 1
                best_solution = {
                    'max_dist': current_dist,
                    'stdout': solution['stdout'],
                    'time': time if time <= timeout else timeout
                }
                print(f"Valid solution found: {current_dist}")
            else:
                upper = current_mid - 1

        elif solution['status'] == 'unsat':
            lower = current_mid + 1

        elif solution['status'] == 'timeout':
            break
    
    return best_solution,time


def solve_smt_file(solver, smt_file, timeout):
    result = {
        'status': 'error',
        'max_dist': None,
        'stdout': '',
        'time': timeout  # Default value
    }

    try:
        start_time = timer()
        cmd = [solver['executable']] + solver.get('options', []) + [smt_file]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            stdout, _ = process.communicate(timeout=timeout)
            end_time = timer()
            result['stdout'] = stdout
            result['time'] = end_time - start_time  # Measured real time
            if 'unsat' in stdout:
                result['status'] = 'unsat'
            elif 'sat' in stdout:
                result['status'] = 'sat'
            else:
                result['status'] = 'unknown'
 
        except subprocess.TimeoutExpired:
            end_time = timer()
            process.kill()
            stdout, _ = process.communicate()
            result['time'] = timeout  # Measured real time
            logger.warning(f"Timeout reached for {os.path.basename(smt_file)}")
            result['status'] = 'timeout'   


        return result

    except Exception as e:
        logger.error(f"Generic error: {str(e)[:200]}")
        return result


def solve(instances,solver,model_name=None,timeout=300):


    config = {
        "z3" : {
            "name": "z3",
            "executable": "z3",
            "options": ["-smt2"]
        },
        "cvc4" : {
            "name": "cvc4",
            "executable": "cvc4",
            "options": ["--produce-models", "--incremental"]
        },
        "cvc5": {
            "name": "cvc5",
            "executable": "cvc5",
            "options": ['--produce-models', '--incremental']
        }
    }

    smtlib_dir =  "SMT/SMT2_FILES"
    smt_file = os.path.join(smtlib_dir, str(instances) + '.smt2')
    output_dir =  "SMT/tmp"
    os.makedirs(output_dir, exist_ok=True)

    logger.info(f"\n{'='*40}\nProcessing file: {instances}\n{'='*40}")


    logger.info(f"\n{'-'*20}\nProcessing with solver: {solver}\n{'-'*20}")
    try:
        best_solution,time = optimize_max_dist(config[solver], smt_file, output_dir, timeout)
        if best_solution:
            logger.info(f"Optimization completed: {best_solution}")
            solver_result = parse_output(best_solution['stdout'], math.floor(time))
            result = solver_result
        else:
            logger.warning("No optimal solution found")
            result = {'time': 300,'optimal': False,'obj': None, 'sol': None}

    except Exception as e:
        result = {'time': 300,'optimal': False,'obj': None, 'sol': None}
        return result   
    else:
        return result



if __name__ == "__main__":
    solve()

