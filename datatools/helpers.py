import json

def jl_ids(file):
    return [json.loads(line.strip())['id'] for line in open(file)]

def jl_packs(file):
    return [json.loads(line.strip()) for line in open(file)]
    
        