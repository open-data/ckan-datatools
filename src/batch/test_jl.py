from datetime import date
import json
from collections import Counter
import pickle
xml_records = pickle.load(open('xrecords.pkl','rb'))

def jl_report(file):
    #print xml_records
    jl_records=[]
    cnt=Counter()
    lines = [line.strip() for line in open(file)]
    for  i,line in enumerate(lines):
        p = json.loads(line)
        jl_records.append(p['id'])
        
        cnt['number of records']+=1
        cnt[p['owner_org']]+=1
        
    for i in cnt.items():
        print i

    
def compare_with_xml():
    xml_enbi=[i[1].lower() for i in xml_records if i[0] != "French"]
    print len(jl_records),len(xml_records), len(xml_enbi)
    print jl_records[1], xml_enbi[1]
    diff = [item for item in xml_enbi if item not in jl_records]
    print len(diff)
    for d in diff:
        print d
    pickle.dump(diff, open('diff.pkl','wb'))
        
    

#    print set(xml_enbi)
#    print len(xmlset)

if __name__ == "__main__":

    load_dir = '/Users/peder/dev/goc/LOAD'
    input_file =  "{}/pilot-{}.jl".format(load_dir,date.today()) 
    jl_report(input_file)

    