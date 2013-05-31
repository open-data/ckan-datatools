import sys
import os
import ckanapi
import json


server='http://localhost:5000'
key='76ec7af1-7fed-4934-b8e4-d896306f403a'

def delete_packs(file):
    ids = [line.strip() for line in open(file)]

    demo = ckanapi.RemoteCKAN(server, api_key=key)
    for id in ids:
        try:
            print id, demo.action.package_delete(id=id)['success']
        except ckanapi.NotFound:
            print id, "not found"
     

if __name__ == "__main__":
    
    ''' Delete 146 old CANSIM records '''
    delete_packs('cansim.delete')
    
    ''' Delete 56 records with the french IDs that were mistakenly entered '''
    delete_packs('french_ids.delete')
    
    
    
