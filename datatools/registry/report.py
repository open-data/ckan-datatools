import sys
import ckanapi  
from pprint import pprint
from ckanext.canada.metadata_schema import schema_description as schema

''' 
    Report for Andrew Makus to determine what records have been amended on the registry; 
    these must not be overwritten by a new load 
    
    Use an ID dump from the registry, produced June 10, 2013
'''

if __name__ == "__main__":
    work_dir="/Users/peder/dev/goc/makus-report/"
    registry_ids=work_dir + "registry-june10"
#    f = open(registry_ids,'r') # open in read mode
#    data = f.read()
#    ids = eval(data)
#    print len(ids)
    
    registry = ckanapi.RemoteCKAN('http://registry.statcan.gc.ca')
    activity_list =  registry.action.recently_changed_packages_activity_list()
    users = registry.action.user_list()
    
    pprint(users['result'])

    for result in activity_list['result']:
        
        pack = result['data']['package']
        print pack['title']
        print pack['id']
        print schema.dataset_field_by_id['owner_org']['choices_by_pilot_uuid'][pack['owner_org']]['eng']
