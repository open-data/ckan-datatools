import os
import sys
import json
import pickle
import ckanapi  
import warnings


'''
 	Get a list of touched ids from the registry
'''


def standard_users(endpoint):
    admins=['64c919b6-a26e-414e-b5f8-12a167a6e863','d590b028-540b-435f-9aa6-2edd9a35afee']
    return [user['name'] for user in endpoint.action.user_list() if user['id'] not in admins]


def users_report(endpoint):
    def display(record):
        print "{},{},{},{}".format(user['name'],user['id'],user['fullname'],user['number_administered_packages'])
    
    [display(user) for user in endpoint.action.user_list()['result']]
        
def activities_for_user(endpoint,user):

    # makus user id is ac12cb42-117d-4d68-8098-66a942d1c17f
    activity_list =  endpoint.action.user_activity_list(id=user,limit=2000)
    activities=[]
    for result in activity_list:
        try:
            pack = result['data']['package']

            activities.append(pack['id'])
        except KeyError:
            ''' No more packages left '''
            break
            pass
       
    id_set=set(activities)
    print user, "has", len(activities), "activities in", len(id_set), "packages."
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
    last_time=datetime(2013,25,6,0,0)
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

def find_touched_registry_packs():
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
    pickle.dump(set(new_ids), open('touched_in_registry-july5.pkl','wb'))    
    
def download_touched_registry_packs():

    touched = pickle.load(open('touched_in_registry.pkl','rb'))
    print "downloading", len(touched)
    
    linkfile ="touched-registry-files.jl"
    file = open(os.path.normpath(linkfile), "wb")
    errors=open(os.path.normpath('api_load_errors.log'),"wb")
    registry = ckanapi.RemoteCKAN('http://registry.statcan.gc.ca',apikey='4c57004e-fe2a-496d-8bef-8dbe98ba91e4')
    for i, id in enumerate(touched):
        
        try:
           package = registry.action.package_show(id=id)['result']
           print i,package['id']
           # Write the package to a file
           file.write(json.dumps(package) + "\n"); 

        except:
            errors.write("{}, Error, {}\n".format(i,id))
            print "ERROR ?",id
            
    print "Finished, thanks for your patience"
if __name__ == "__main__":
    find_touched_registry_packs()
    download_touched_registry_packs()


    
    