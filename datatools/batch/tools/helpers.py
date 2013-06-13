import json

def jl_ids(file):
    return [json.loads(line.strip())['id'] for line in open(file)]
        