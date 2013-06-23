import json
from datatools import helpers

''' 
        Combine matched and single pilot jl files, 
        remove environment canada records, then add new ec records (210)
'''
def depts():
    ''' Generator '''
    for r in records:
        if r['owner_org'] != 'ec':
            yield r

def jlrecords(file):        
    return [json.loads(line) for line in open(helpers.load_dir(0)+file)]   

if __name__ == "__main__":
    # Combine pilot records but exlude original from enviroment canaada

    pilot=jlrecords("pilot-bilingual.jl")
    pilot.extend(jlrecords("pilot-matched.jl"))
    
    records=[r for r in pilot if r['owner_org'] != "ec"]
    #records.extend(jlrecords("ec.jl"))
    Need to combine more record types and document before I can tag this
    Also, figure if there are more files like : file:///temp/d13c729f-1ff0-41b5-9546-17b62593c2b8.xml
    load_file=open(helpers.load_dir(0)+"pilot.jl","w")  
    
    [load_file.write(json.dumps(r)+"\n") for r in records]