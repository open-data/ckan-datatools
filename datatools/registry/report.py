import os
import sys
import json
import pickle
import ckanapi  
import socket 
import warnings
import urllib2
from collections import Counter
from datetime import datetime, date, time
from pprint import pprint
from ckanext.canada.metadata_schema import schema_description as schema
#from datatools import helpers

''' 
    Report for Andrew Makus to determine what records have been amended on the registry; 
    these must not be overwritten by a new load 
    
    Use an ID dump from the registry, produced June 10, 2013
'''



def new_registry_packages():
    ''' Count packages that have been created and / or updated by  account holders at registry 
        and pickle it for later use
    '''
    work_dir="/Users/peder/dev/goc/makus-report/"
    registry_ids=work_dir + "registry-june10"
    registry = ckanapi.RemoteCKAN('http://registry.statcan.gc.ca')
    new_ids=[]
    users=standard_users(registry)
    
    for user in users:
        ids = activities_for_user(registry,user)
        new_ids.extend(ids)
        print len(new_ids)
        # change to a set to avoid activity duplicates
    # change to a set to avoid activity duplicates between people
    print "-----------"
    print len(new_ids), len(set(new_ids))
    pickle.dump(set(new_ids), open('touched_in_registry.pkl','wb'))

def all_load_ids():
    print "Collect all ids from load files"
    all=[]
    dir='/Users/peder/dev/OpenData/combined_loads/2013-06-12/'
    for (path, dirs, files) in os.walk(os.path.normpath(dir)):
        for n,file in enumerate(files):
            all.extend(helpers.jl_ids(dir+file))
    len(all)
    return(all)
 



def touched_in_registry():
    '''  Make sure there are no duplicates in the activity list record set  from registry '''
    touched = pickle.load(open('touched_in_registry.pkl','rb'))
    print "Touched records", len(touched)
    print "Checking for duplicates"
    cnt = Counter()
    for t in touched:
        cnt[t]+=1
        print t
        
    print len(set(touched))
    print cnt.most_common()
    
           
def registry_records_not_in_load():
    ''' Count records that are found by new_registry_packages() but are not in the ids of the load files.

    '''
    changed=[]
    new=[]
    altered_ids = pickle.load(open('touched_in_registry.pkl','rb'))
    all_ids = all_load_ids()
    print len(all_ids)
    for id in all_ids:
        if id in altered_ids:
            changed.append(id)
            
    print "Existing IDs that have been changed", len(changed)
    pickle.dump(changed, open('changed_after_load.pkl','wb'))
    

def new_in_registry_report():
    ''' id and title of records that have been newly created on registry '''
    altered_ids = pickle.load(open('new_in_registry.pkl','rb'))
    existing_but_changed_ids=pickle.load(open('changed_after_load.pkl','rb'))
    
    new_ids=set(altered_ids).difference(set(existing_but_changed_ids))
    print len(new_ids)
    print len(set(new_ids))    
    departments=schema.dataset_field_by_id['owner_org']['choices_by_pilot_uuid']
    # open the jl dump
    report=[]
    for i,line in enumerate(open('/Users/peder/dev/OpenData/analysis/touched-registry-files.jl', 'r')):
       
        pack = json.loads(line)

        if pack['id'] in new_ids:
            owner_org = departments[pack['owner_org']]['eng']
            report.append((pack['id'],owner_org,pack['title']))
    
    
    print len(report),len(set(report)), "No duplicates"
    
    for i,line in enumerate(sorted(report)):
        print  line[0],line[1],line[2]

       

def changed_on_registry_report():
    ''' Analyze how files have changed on the registry to see if and how they can be updated '''
    
    changed_packs=[]
    changed_ids=pickle.load(open('changed_after_load.pkl','rb'))
    for line in open('/Users/peder/dev/OpenData/analysis/changed-registry-files.jl', 'r'):
        pack = json.loads(line)
        if pack['id'] in changed_ids:
            print pack['title']

def check_for_duplicates():
    ids=[]
    for line in open('/Users/peder/dev/OpenData/analysis/changed-registry-files.jl', 'r'):
        pack = json.loads(line)
        ids.append(pack['id'])
    
    print len(ids)
    print len(set(ids))
     
if __name__ == "__main__":
    #touched_in_registry()
    #new_registry_packages()
    #download_changed_registry_packs()
    #check_for_duplicates()
    #changed_on_registry_report()
    new_in_registry_report()
    #registry_records_not_in_load()
    
    

    