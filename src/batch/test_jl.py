from datetime import date
import json
from collections import Counter
import pickle
from pprint import pprint
from data  import registry
import sys
xml_records = pickle.load(open('xrecords.pkl','rb'))

def jl_ids(file):
    jl_records=[]
    lines = [line.strip() for line in open(file)]
    for  i,line in enumerate(lines):
        p = json.loads(line)
        jl_records.append(p['id'])
    return jl_records
        
def jl_records(file):
    jl_records=[]
    lines = [line.strip() for line in open(file)]
    for  i,line in enumerate(lines):
        p = json.loads(line)
        jl_records.append(p)
    return jl_records

def jl_records_dict(file):
    jl_records={}
    lines = [line.strip() for line in open(file)]
    for  i,line in enumerate(lines):
        p = json.loads(line)
        jl_records[p['id']]=p
    return jl_records

def jl_report(file):
    #print xml_records
    cnt=Counter()
    for p in jl_records(file):
        cnt['number of records']+=1
        cnt[p['owner_org']]+=1
        
    for i in cnt.items():
        print i
        
        
def title_diff(old,new):
    #print xml_records
    cnt=Counter()
#    old = jl_records(old)
#    new = jl_records(new)
#    print len(old),len(new)
    i =1
    n=1
    old=jl_records(old)
    new=jl_records(new)
    print len(old), len(new)
    for record in new:
        found=False
        for orecord in old:
            if record['title'] == orecord['title'] or record['title'] in orecord['title']:
#               print i,record['title']
               i+=1
               found=True
               break
        if not found:
            i+=1
            n+=1
            #print n, i, "Can't find", record['id']
            print record['id']
            

def id_diff(old,new):

    baseline_cnt=Counter()
    baseline_file_ids=jl_ids(old)
    latest_file_ids=jl_ids(new)
    print "------    Baseline JL File  -------"
    print "Baseline JL File Size:", len(baseline_file_ids)
    
    # Look for duplicates
    for id in baseline_file_ids: baseline_cnt[id]+=1
       
    print "Baseline unique ids:", len(baseline_cnt)
    print "Baseline duplicates:", len([item for item in baseline_cnt.items() if item[1]>1])
    
    
    latest_cnt=Counter()
    print "------    Latest JL File -------"
    print "Latest JL File Size:", len(latest_file_ids)
    
    # Look for duplicates
    for id in latest_file_ids: latest_cnt[id]+=1
       
    print "New file unique ids:", len(latest_cnt)
    print "New file duplicates:", len([item for item in latest_cnt.items() if item[1]>1])   
    
    '''
        Ensure that both files have the same ids, 
        minus 26 duplicates, plus 20 new files 
        If the numbers don't make sense, something may have 
        gone wrong.
        This analysis can be caried out by counting ids in both files with one counter
    
    '''
    both_cnt=Counter()
    for id in baseline_file_ids: both_cnt[id]+=1
    print len(both_cnt)
    for id in latest_file_ids: both_cnt[id]+=1
    print len(both_cnt)
    
    print "Number of unique files the were not doubled in counter:", len([id for id in both_cnt.items() if id[1]==1])
    total=0
    for item in both_cnt.items():
        if item[1]==1: 
            total+=1
            print total, item[0] 
    
    
    ''' Which of these wayward files are in the baseline ? '''
    
    baseline_records = jl_records_dict(old)
    latest_records = jl_records_dict(new)
    n=1
    for item in both_cnt.items():
        if item[1]==1: 
            try:
                title = baseline_records[item[0]]['title']
                print n,"OLD",title ,item[0]
                n+=1
            except KeyError:
                print n, "NEW", latest_records[item[0]]['title'],item[0]
                n+=1
            except:
                print "SOMETHING ELSE HAPPENED"
        
    
   
    
           
def compare_with_xml():
    xml_enbi= [i[1].lower() for i in xml_records if i[0] != "French"]
    print len(jl_records),len(xml_records), len(xml_enbi)
    print jl_records[1], xml_enbi[1]
    diff = [item for item in xml_enbi if item not in jl_records]
    print len(diff)
    for d in diff:
        print d
    pickle.dump(diff, open('diff.pkl','wb'))

def analyze_keywords(file):
    for i,record in enumerate(jl_records_dict(file).values()):
        print "---    {}   ---".format(i)
        print record['keywords']
        print record['keywords_fra']
        
        if i>300:sys.exit()
        
      
def compare_with_registry(file):
    '''
     The titles that seem different between the old and new jl files 
     they need to be checked against what's in the registry ids to ensure 
    that they are in fact new
    
    '''
    new_records=jl_records_dict(file)
    # The titles in the new .jl file that does not seem to be in the baselined .jl file
    title_diffs = [line.strip() for line in open("diff.log")]
    
    print "Number of records that *may* be new or where the title may be different", len(title_diffs)
    count =1 
    found_match =[]
    for id in registry.ids:
        
        if id in title_diffs:
            print "IT's there: ", count,id
            found_match.append(id)
            count+=1
    # These id's are not in the registry       
    not_in_reg= set(title_diffs).difference(set(found_match))
    print len(not_in_reg)
    for n in not_in_reg:
       print new_records[n]
        
    
    reg = registry.ids
    print "Registry Size" , len(reg)
    print "Registry Size" ,len(set(reg))
    jl=jl_ids(file)
    print "JL Size", len(jl)
    print "JL Set Size", len(set(jl))
    regset=set(reg)
    jlset=set(jl)
    
    cnt = Counter()
    for j in jl:
        cnt[j]+=1
    print "JL total size and set size is due to duplicates:"
    for i in cnt.items():
        if i[1]>1:
            print i

#    print regset.issubset(jlset)
#    print jlset.issubset(regset)
#    diff = jlset.difference(regset)
    #pprint(diff)
    #pprint(regset.difference(jlset))
    #pprint (regset.intersection(jlset))
    print "Intersection", len(regset.intersection(jlset))
    print "Union", len(regset.union(jlset))
    print "Difference", len(regset.difference(jlset))
    #pprint(regset.union(jlset) - regset.intersection(jlset))

def repair_jl(file):
    '''
     The titles that seem different between the old and new jl files 
     they need to be checked against what's in the registry ids to ensure 
    that they are in fact new
    
    '''
    lines = [line.strip() for line in open(file)]
    for  i,line in enumerate(lines):
        print json.dumps(eval(line))

if __name__ == "__main__":
    
    load_dir = '/Users/peder/dev/goc/LOAD'
    base_load_file = '/Users/peder/source/ckan-datatools/data/pilot-2013-05-14.jl'
    input_file =  "{}/pilot-{}.jl".format(load_dir,date.today()) 
    broken_file="/Users/peder/dev/goc/LOAD/new_records_may_17.jl"
    #repair_jl(broken_file)
    #analyze_keywords(input_file)
    
    #compare_with_registry(input_file)
    
    #jl_report(input_file)
    #title_diff(base_load_file,input_file)
    id_diff(base_load_file,input_file)
    
    