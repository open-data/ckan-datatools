import os
import sys
import json
import pickle
import ckanapi
import socket
import warnings
import urllib2
import difflib
from collections import Counter
from datetime import datetime, date, time
from pprint import pprint
from ckanext.canada.metadata_schema import schema_description as schema
from datatools import helpers

'''
    Report for Andrew Makus to determine what records have been amended on the registry;
    these must not be overwritten by a new load
    
    Use an ID dump from the registry, produced June 10, 2013
'''

def all_load_ids():
    print "Collect all ids from load files"
    all=[]
    dir='/Users/peder/dev/OpenData/combined_loads/2013-06-12/'
    for (path, dirs, files) in os.walk(os.path.normpath(dir)):
        for n,file in enumerate(files):
            print file
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
    touched_ids = pickle.load(open('touched_in_registry.pkl','rb'))
    all_ids = all_load_ids()
    print len(all_ids)
    for id in all_ids:
        if id in touched_ids:
            changed.append(id)
    
    print "Existing IDs that have been changed", len(changed)
    new = set(touched_ids) - set(changed)
    print new
    pickle.dump(new, open('not_in_load.pkl','w'))
    pickle.dump(changed, open('in_load_but_changed.pkl','w'))

def new_in_registry_report():
    ''' id and title of records that have been newly created on registry '''
    not_in_load = pickle.load(open('not_in_load.pkl','rb'))
    print "Checking for duplicate IDs"
    print len(not_in_load)
    print len(set(not_in_load))
    #print not_in_load
    departments=schema.dataset_field_by_id['owner_org']['choices_by_pilot_uuid']
    # open the jl dump
    report=[]
    for i,line in enumerate(open('/Users/peder/dev/OpenData/analysis/touched-registry-files.jl', 'r')):
        
        pack = json.loads(line)
        #print pack
        if pack['id'] in not_in_load:
            try:
                owner_org = departments[pack['owner_org'].upper()]['eng']
            except:
                owner_org = pack['owner_org']
            
            report.append((pack['id'],owner_org,pack['title']))
    
    
    print len(report),len(set(report)), "No duplicates"
    
    for i,line in enumerate(sorted(report)):
        print  u"{}\t{}\t{}".format(line[0],line[1],line[2]).encode('utf-8')
       

def search_load_files(id,include_geogratis=False):
    loaddir ='/Users/peder/dev/OpenData/combined_loads/2013-06-12/'
    search_files=['pilot-bilingual.jl','pilot-matched.jl']
    for file in search_files:
        
        if id in helpers.jl_ids(loaddir+file):return file


def load_dict():
        
        ''' Create dict of all packs with id as key '''
        packs={}
        print "Getting load files"
        loaddir ='/Users/peder/dev/OpenData/combined_loads/2013-06-12/'
        search_files=['pilot-bilingual.jl','pilot-matched.jl']
        for file in search_files:
            load = helpers.jl_packs(loaddir+file)
            for pack in load:
                packs[pack['id']]=pack
            print len(load)
        return packs
    
    
def changed_on_registry_report():
    ''' Analyze how files have changed on the registry to see if and how they can be updated '''
    records=load_dict()
    print len(records)
    changed_ids=pickle.load(open('in_load_but_changed.pkl','rb'))
    diff_packs=[]
    for line in open('/Users/peder/dev/OpenData/analysis/touched-registry-files.jl', 'r'):
        pack = json.loads(line)
        id=pack['id']
        if id in changed_ids:
            try:
                #print records[id]['title']
                diff_packs.append((records[id],pack))
            except KeyError:
                print "NOT FOUND" , pack['title']
    
    
    print(len(diff_packs))

    for p in diff_packs:
        print "----------{}----------".format(p[0]['id'])
        for key in p[0].keys():
            
            try:
                load=p[0][key]
                registry=p[1][key]
                
                assert load==registry, 'They are not equal'
                print "OK",key
            except AssertionError:
                print "LOAD RECORD ", key, " >", load 
                print "REG RECORD ", key, " >", registry
                pass
            except KeyError:
                print "missing key", key
        
        sys.exit()
        '''
        print "-------"
        print p[0]['title'],"::::", p[1]['title']
        d1=difflib.SequenceMatcher(None, " abcd", "abcd abcd")
        print d1
        d=difflib.Differ()
        result = list(d.compare(str(p[0]['title']), str(p[1]['title'])))
        pprint(result)
        sys.exit()
        '''
        

def check_for_duplicates():
    ids = [json.loads(line)['id'] for line in open('/Users/peder/dev/OpenData/analysis/touched-registry-files.jl', 'r')]

    print len(ids), len(set(ids))

def records():
    file = open('/Users/peder/dev/OpenData/analysis/touched-registry-files.jl', 'r')
    yield json.loads(file.next())['id']

def registry_report():
    print records.next()
    print records.next()
    
if __name__ == "__main__":
    registry_report()
    #touched_in_registry()
    #new_registry_packages()
    #download_changed_registry_packs()
    #check_for_duplicates()
    #changed_on_registry_report()
    #new_in_registry_report()
    #registry_records_not_in_load()
    

    
    