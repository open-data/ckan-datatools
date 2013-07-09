import os
import json

def pilot_records():
    ''' A generator that provides access to all ids in .jl load files '''
    dir='/Users/peder/dev/OpenData/combined_loads/2013-06-20/'
    for (path, dirs, files) in os.walk(os.path.normpath(dir)):
        for n,file in enumerate(files):
            if ".jl" in file and "nrcan" not in file:
                for line in open(path+"/"+file):  
                    record=json.loads(line.strip())
                    yield (record['id'],record)