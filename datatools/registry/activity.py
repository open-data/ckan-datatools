import json
import pickle
import ckanapi  
from pprint import pprint
from datetime import datetime


def activities(endpoint):
    
    
    begin = datetime(2013,1,6,0,0).isoformat()
    last_time = datetime(2013,1,16,0,0).isoformat()
    print begin, last_time
    def get_data(last_time):
        # Use standard recursion, eg. Make the problem smaller on each recurse
        # Recursion base case test. If true, exit from loop, otherwise continue
        if last_time == begin:
            return True
        else:
            data = endpoint.action.changed_packages_activity_list_since(since_time=last_time)
            packs = data['result']
            print len(data['result'])
        
            for p in packs:
                print p['timestamp']
                last_time=p['timestamp']
         
    while True:
        get_data(last_time)
if __name__ == "__main__":
    print "Activity Report"
    registry = ckanapi.RemoteCKAN('http://registry.statcan.gc.ca')
    activities(registry)
    
  