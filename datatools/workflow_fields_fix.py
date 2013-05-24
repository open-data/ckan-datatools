import sys
import os
import ckanapi
#from jsonpath import jsonpath
from pprint import pprint 
import datatools

def update_all_fields(ckansite):
    print "Working with data at  ", ckansite, ":    "
    pack_ids = datatools.registry_package_list()
    registry = ckanapi.RemoteCKAN('http://registry.statcan.gc.ca/')
    for i,pack_id in enumerate(pack_ids):
        # 1. Get the package
        pack = registry.action.package_show(id=pack_id)['result']
        #pprint(pack)
        pprint(pack['ready_to_publish'])
        #pprint(pack['portal_release_date'])
        # 2.  Update the fields
        pack['ready_to_publish']=True
        #pack['
        #pprint(pack['ready_to_publish'])
        # 3. Write the package
        #ckan.logic.action.create.package_create(context, data_dict)
        # 4. Get the package as pack_after
        # 5. Check ensure evething is ok by comparing pack and pack_after
        for key, value in pack.items():
            print key
            if key == "resources": continue
            # deal with that pesky '\u2013' dash char
            #print key, (u"%s" % value).encode('utf8') 
        sys.exit() 
 

if __name__ == "__main__":
    #update_all_fields("http://data.statcan.gc.ca/data")
    #update_all_fields("http://registry.statcan.gc.ca")
    update_all_fields("http://localhost:5000")