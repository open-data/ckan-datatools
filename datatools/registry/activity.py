import json
import pickle
import ckanapi  
from pprint import pprint
from datetime import datetime


def activities(endpoint):
    
    
    begin = datetime(2013,06,20,0,0).isoformat()
    last_time = datetime(2013,06,23,0,0).isoformat()
    activity_list=[]
    def get_data(last_time):

        # Use standard recursion, eg. Make the problem smaller on each recurse
        # Recursion base case test. If true, exit from loop, otherwise continue

        data = endpoint.action.activity_list_from_user_since(since_time=last_time,user_id='3cf66410-f82f-4b47-8119-e0603c743ecc')
        #data = endpoint.action.changed_packages_activity_list_since(since_time=begin)
        if not data: 
            return 
        for d in data:
            activity_list.append(d)
            last_time=d['timestamp']
            
        return last_time
         
    while last_time:
        last_time = get_data(last_time)
        
    return activity_list
        
if __name__ == "__main__":
    print "Activity Report"
    registry = ckanapi.RemoteCKAN('http://registry.statcan.gc.ca')
    #local = ckanapi.RemoteCKAN('http://localhost:5000')
    pprint (activities(registry))
    
    
  