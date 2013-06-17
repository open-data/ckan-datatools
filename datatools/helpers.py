import json
from datetime import date, timedelta

def jl_ids(file):
    return [json.loads(line.strip())['id'] for line in open(file)]

def jl_packs(file):
    return [json.loads(line.strip()) for line in open(file)]  

def load_dir(days=0):
    return  "/Users/peder/dev/OpenData/combined_loads/{}/".format(date.today()-timedelta(days))