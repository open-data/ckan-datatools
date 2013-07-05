import sys
import os
import ckanapi
import json


server='http://registry.statcan.gc.ca'
key=None

def delete_packs(file):
    ids = [line.strip() for line in open(file)]

    demo = ckanapi.RemoteCKAN(server, api_key=key)
    for i in ids:
        id = i.lower()
        try:
            print id, demo.action.package_delete(id=id)['success']
        except ckanapi.NotFound:
            print id, "not found"
     

if __name__ == "__main__":
    
    # Ross will pass API key 
    key=sys.argv[1]
    ''' Delete a few files that were duplicated on release data June 18, 2013 '''
    delete_packs('../data/deletes/ec_old.delete')
    
    ''' Delete 16,842 old Geogratis records that will have new package ids'''
    #delete_packs('../data/deletes/old_geo_ids.delete')

    ''' Delete 146 old CANSIM records '''
    #delete_packs('../data/deletes/cansim.delete')
    
    ''' Delete 56 records with the french IDs that were mistakenly entered '''
    #delete_packs('../data/deletes/french_ids.delete')
    
    
    
