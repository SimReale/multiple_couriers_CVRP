import json
import os 
import re 
from SMT.loggin_config import *

logger = logging.getLogger(__name__)



def extract_initial_bounds(content):
    """
    Extracts the initial lower and upper bounds for max_dist from the SMT content.
    Returns (lower, upper)
    """
    lower = None
    upper = None
    
    lower_pattern = re.compile(r'\(assert\s+\(>= max_dist\s+(\d+)\)\)')
    upper_pattern = re.compile(r'\(assert\s+\(<= max_dist\s+(\d+)\)\)')
    
    for line in content.split('\n'):
        stripped = line.strip()
        lower_match = lower_pattern.match(stripped)
        upper_match = upper_pattern.match(stripped)
        
        if lower_match:
            lower = int(lower_match.group(1))
        elif upper_match:
            upper = int(upper_match.group(1))
    
    if lower is None or upper is None:
        raise ValueError("max_dist constraints not found in the SMT file")
    return lower, upper


def parse_output(output, time):
    result = {
        "time": time if time <= 300 else 300,
        "optimal": False,
        "obj": 0,
        "sol": []
    }

    try:
        max_dist = 0
        couriers = {}

        # Extraction of max_dist with regex
        max_dist_match = re.search(r'\(\(\s*max_dist\s+(\d+)\s*\)\)', output)
        if max_dist_match:
            max_dist = int(max_dist_match.group(1))

        # Extraction of courier routes 
        for line in output.split('\n'):
            line = line.strip()
            if 'courier_' in line and 'true' in line:
                match = re.search(r'courier_(\d+)_(\d+)_(\d+)', line)
                if match:
                    try:
                        courier_id = int(match.group(1))
                        from_node = int(match.group(2))
                        to_node = int(match.group(3))
                        
                        if courier_id not in couriers:
                            couriers[courier_id] = []
                        couriers[courier_id].append({'from': from_node, 'to': to_node})
                    except ValueError:
                        logger.error("Invalid courier ID format")

        # Reconstruction of paths 
        if couriers:
            all_nodes = {node for c in couriers.values() 
                        for t in c 
                        for node in (t['from'], t['to'])}
            if all_nodes:
                depot = max(all_nodes)
                print('depot' + str(depot))
                for _, transitions in couriers.items():
                    path = []
                    current_node = depot
                    visited = set()
                    
                    while current_node in {t['from'] for t in transitions}:
                        if current_node in visited:
                            break
                        visited.add(current_node)
                        
                        transition = next((t for t in transitions if t['from'] == current_node), None)
                        if transition:
                            if current_node != depot:
                                path.append(current_node)
                            current_node = transition['to']
                    
                    path = [x+1 for x in path if x != depot]
                    result["sol"].append(path)

        result["obj"] = max_dist
        result["optimal"] = time < 300

    except Exception as e:
        logger.error(f"Error in parsing: {str(e)}")

    return result
