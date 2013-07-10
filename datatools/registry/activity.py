import json
import pickle
import ckanapi  
from pprint import pprint
from datetime import datetime


def activities(endpoint,user_id):
    
    
    begin = datetime(2013,06,20,0,0).isoformat()
    last_time = datetime(2013,06,23,0,0).isoformat()
    activity_list=[]
    def get_data(last_time,user_id):

        # Use standard recursion, eg. Make the problem smaller on each recurse
        # Recursion base case test. If true, exit from loop, otherwise continue

        data = endpoint.action.activity_list_from_user_since(since_time=last_time,user_id=user_id)
        #data = endpoint.action.changed_packages_activity_list_since(since_time=begin)
        if not data: 
            return 
        for d in data:
            activity_list.append(d)
            last_time=d['timestamp']
        return last_time
         
    while last_time:
        last_time = get_data(last_time,user_id)
        
    return activity_list
        
if __name__ == "__main__":
    print "Activity Report"
    registry = ckanapi.RemoteCKAN('http://registry.statcan.gc.ca',apikey='4c57004e-fe2a-496d-8bef-8dbe98ba91e4')
    public= ckanapi.RemoteCKAN('http://www.data.gc.ca/data')
    #local = ckanapi.RemoteCKAN('http://localhost:5000')
    #Andrew Makus user id
    #user_id='ac12cb42-117d-4d68-8098-66a942d1c17f'
    #pprint (activities(registry,user_id))
    
    ''' Activities by organization - simulates curl http://registry.statcan.gc.ca/api/action/organization_activity_list -d '{"id": "cbsa-asfc"} 

    data = registry.action.user_activity_list(id='ac12cb42-117d-4d68-8098-66a942d1c17f')
    for n,d in enumerate(data):
        print n+1,d['activity_type'], d['data']['package']['title']
        
    '''
    data = public.action.package_search(fq="organization:statcan")
    print len(data)
    
  