#-*- coding:UTF-8 -*-
import sys
import json
import ckanapi
#import resource
from pprint import pprint
from ckanext.canada.metadata_schema import schema_description


'''
    For every pilot data field that was entered into registry, category_type and subject is missing.
    
    Procedure for fixing this:
    
    1. For every id grab these values from Pilot XML and create list of tuples:
    [(id, subjec, category_type),...
    2. For every tuple:
        i. Get package in registry
        ii.Check to see if the two fields are empty, if so, update them
        iii. Write the package back.
    
'''


if __name__ == "__main__":

    pilot_jl = '/Users/jakoped/Documents/OpenData/july2013/pilot-2013-06-09.jl'
    registry = ckanapi.RemoteCKAN('http://registry.statcan.gc.ca',apikey='4c57004e-fe2a-496d-8bef-8dbe98ba91e4')
    
    ids=[]
    for i, line in enumerate(open(pilot_jl)):
        id = json.loads(line)['id']
        org = json.loads(line)['owner_org']
       
        
        if org=="ec":
            try:
                pack = registry.action.package_show(name_or_id=id.lower())
                print pack['id'], pack['owner_org'], pack['catalog_type']
                result = registry.action.package_delete(id=id)
                print result
            except ckanapi.NotFound:
                print id, "Not found"
            except:
                raise
                
                


    