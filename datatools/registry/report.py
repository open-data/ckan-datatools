import os
import sys
import json
import pickle
import ckanapi  
import socket 
import warnings
import urllib2
from datetime import datetime, date, time
from pprint import pprint
from ckanext.canada.metadata_schema import schema_description as schema
#from datatools.batch.tools import helpers
''' 
    Report for Andrew Makus to determine what records have been amended on the registry; 
    these must not be overwritten by a new load 
    
    Use an ID dump from the registry, produced June 10, 2013
'''


def users_report(endpoint):
    users = endpoint.action.user_list()
    for user in users['result']:
        print "{},{},{},{}".format(user['name'],user['id'],user['fullname'],user['number_administered_packages'])

def standard_users(endpoint):
    admins=['64c919b6-a26e-414e-b5f8-12a167a6e863','d590b028-540b-435f-9aa6-2edd9a35afee']
    return [user['name'] for user in endpoint.action.user_list()['result'] if user['id'] not in admins]

        
def activities_for_user(endpoint,user):

    # makus user id is ac12cb42-117d-4d68-8098-66a942d1c17f
    activity_list =  endpoint.action.user_activity_list(id=user,limit=2000)
    ids=[]
    for result in activity_list['result']:
        try:
            pack = result['data']['package']

            ids.append(pack['id'])
        except KeyError:
            ''' No more packages left '''
            break
            pass
       
    id_set=set(ids)
    print user, "has", len(id_set), "packages"
    return list(id_set)
    

def all_activity_for_user(endpoint,user):
    seen_package_id_set=set()
    def doit(since_time, seen_id_set=None):
        
        data = endpoint.action.changed_packages_activity_list_since(since_time=since_time)
       
        if seen_id_set is None:
            seen_id_set = set()

        if not data['result']:
            return None, None
        package_ids = []
        for result in data['result']:
            package_id = result['data']['package']['id']
            if package_id in seen_id_set:
                continue
            seen_id_set.add(package_id)
            package_ids.append(package_id)

            if data['result']:
                since_time = data['result'][-1]['timestamp']
            #print package_ids, since_time
            return package_ids, since_time
        
        
    start_date="2013-04-01"   
    while True:  
        package_ids, next_date = doit(start_date,seen_package_id_set)
        print package_ids, next_date
        if next_date is None:
            return False
        
        len(seen_package_id_set)
        start_date=next_date
        
    print seen_package_id_set
 
def activities(endpoint,user):

    date_object = datetime(2013,1,6,0,0)
    last_time=date_object
    def get_data(last_time):
        data = endpoint.action.changed_packages_activity_list_since(since_time=last_time.isoformat())
    
        packs = data['result']
        print len(data['result'])
        
        for p in packs:
            print p['user_id']
            last_time=p['timestamp']
            print last_time
    print "----------------", last_time
    get_data(last_time)
    print "----------------", last_time
    get_data(last_time)
    # Etc. 

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
    pickle.dump(new_ids, open('new_in_registry.pkl','wb'))
    
def registry_records_not_in_load():
    ''' Count records that are found by new_registry_packages() but are not in the ids of the load files.

    '''
    all=[]
    dir='/Users/peder/dev/OpenData/combined_loads/2013-06-12/'
    for (path, dirs, files) in os.walk(os.path.normpath(dir)):
        for n,file in enumerate(files):
            print file
 
def download_changed_registry_packs():

    # Note the name "new-in_registry" is a misnomer, it should be "changed_in_registry"
    changed = pickle.load(open('new_in_registry.pkl','rb'))
    opener = urllib2.build_opener()
    linkfile ="/temp/changed-registry-files.jl"
    file = open(os.path.normpath(linkfile), "a")
    for id in changed:
        url = "http://registry.statcan.gc.ca/api/rest/dataset/{}".format(id)
        try:
        
           req = urllib2.Request(url)
           f = opener.open(req,timeout=500)
        except HTTPError:
            print "FORBIDDEN", url
        except:
            raise
            
        response = f.read()
        package = json.loads(str(response),"utf-8")
        print package['title']
        # Write the package to a file
        file.write(json.dumps(package) + "\n"); 
    
if __name__ == "__main__":
    download_changed_registry_packs()
    #registry_records_not_in_load()
    
    

    