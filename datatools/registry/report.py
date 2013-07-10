#-*- coding:UTF-8 -*-
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
    Report what records have been amended on the registry;
    these must not be overwritten by a new load
    
    Use an ID dump from the registry, produced June 10, 2013
'''
departments=schema.dataset_field_by_id['owner_org']['choices_by_pilot_uuid']

def pilot_records():
    ''' A generator that provides access to all ids in .jl load files '''
    dir='/Users/peder/dev/OpenData/combined_loads/2013-06-20/'
    for (path, dirs, files) in os.walk(os.path.normpath(dir)):
        for n,file in enumerate(files):
            if ".jl" in file and "nrcan" not in file:
                for line in open(path+"/"+file):  
                    record=json.loads(line.strip())
                    yield (record['id'],record)
    

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
    touched_ids = pickle.load(open('../data/touched_in_registry.pkl','rb'))
    all_ids = all_load_ids()
    print len(all_ids)
    for id in all_ids:
        if id in touched_ids:
            changed.append(id)
    
    print "Existing IDs that have been changed", len(changed)
    new = set(touched_ids) - set(changed)
    print new
    pickle.dump(new, open('../data/not_in_load.pkl','w'))
    pickle.dump(changed, open('../data/in_load_but_changed.pkl','w'))

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
       

def bold(msg):
    return u'\033[1m{}\033[0m'.format(msg).encode('utf-8')

def color(color, msg):
    return u"\033[{}m{}\033[0m".format(color,msg).encode('utf-8')

    
def what_fields_changed():
    
    loaded=dict(record for record in pilot_records())
    print len(loaded)
    load_ids=[id for id,value in loaded.iteritems()]
    touched = dict((json.loads(line)['id'], json.loads(line)) for line in open('../../data/touched-registry-files.jl', 'r'))
    touched_ids = [id for id,value in touched.iteritems()]
    print len(touched_ids)
    new_ids = set(touched_ids) - set(load_ids)
    changed_ids=set(touched_ids)-new_ids
    print "New IDs", len(new_ids)
    print "Changed IDs", len(changed_ids)
    
    
    
    both=[(loaded[id],touched[id]) for id in list(changed_ids)]


    # Important fields that have changed during schema development
    package_fields=[
                    #'ready_to_publish',  
                    #'portal_release_date',
                    'resources',
                    'owner_org',
                    'keywords',
                    'keywords_fra',
                    'data_series_issue_identification',
                    'geographic_region',
                    'spatial',
                    'browse_graphic_url',
                    'endpoint_url',
                    ]
    
    resource_fields=[
                         'url',
                         'format',
                         'size',
                         'name',
                         'name_fra',
                         'language',
                         'resource_type'
                         ]
    
    cnt= Counter()
    new_jl = open("../../data/changed_registry_merge.jl","wb")
    for n,(before, after) in enumerate(both):
        
        print bold(u"{} {} --- {} ---".format(n,before['owner_org'],before['title']))
        #pprint(before)
        for field in package_fields:
            try:
                bef =before[field]
            except KeyError as k:
                print "Load file missing field,", field
                cnt["load missing "+field]+=1
                #continue
            try:
                aft =after[field]
            except KeyError as k:
                print "Registry missing field," ,field
                cnt["registry missing "+field]+=1
                #continue
                
            if bef==aft: 
                pass
            elif field == "resources":
                pass

            else:
                print before[field],after[field]
                #print field,"::", color(32," > "+before[field]), color(31, " > "+after[field])  
            
        ##################   DONE CHECKING FIELDS. FIX REGISTRY FIELDS ##############
        '''
        1. Remove punctuation from keywords list
        2. Add portal_release_date 
        3. Write to new file, fixed_changed_registry.jl
        
        '''
        package_dict=before
        print package_dict['id']
       
       
        for key in before.keys():
            if key == 'resources':
               package_dict['resources']=[]
               for resource in after['resources']:
                   print "------------    RESOURCE"
                   
                   new_resource_dict={}
                   for rkey in resource_fields:
                       try:
                           new_resource_dict[rkey]=resource[rkey]
                       except:
                           print "Resource field n/a", rkey
                   package_dict['resources'].append(new_resource_dict) 
            #-- End Resources --
            else:
                try:
                    new_value=after[key]
                    package_dict[key]=new_value
                except KeyError as e:
                    print key, "does not exist in after", e

            package_dict['ready_to_publish']=False
            package_dict['portal_release_date']='2013-06-18'
            package_dict['keywords']=package_dict['keywords'].rstrip(".")
            package_dict['keywords_fra']=package_dict['keywords_fra'].rstrip(".")
        pprint(package_dict)
  
        new_jl.write(json.dumps(package_dict)+"\n")    
                
        #yield(cnt.items())
        
 
    
if __name__ == "__main__":
    
    #registry_records_not_in_load()
    #what_fields_changed()
    
    ''' Allow user to view a) next record, b) random record,  or c) all records report.
        This will save the script from having to do the heavy lifting of having to continously 
        read the load files 
        
    '''
    what_fields_changed()
    ''' Better than using main is to use the python prompt and create an object '''
    #changed = what_fields_changed()

    '''
    while True:
        r = raw_input("Next (n), Random (r), or Report All (a), Quit (q) > ")
        if r == "n": changed.next()
        if r == "a":print [c for c in changed]
        if r == 'q': sys.exit()
    '''
    
        
        
    #check_for_duplicates()
    #registry_report()
    #touched_in_registry()
    #new_registry_packages()
    #download_changed_registry_packs(
    #new_in_registry_report()
    #registry_records_not_in_load()
    

    
    