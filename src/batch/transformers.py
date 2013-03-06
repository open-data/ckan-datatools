import json
from pprint import pprint 
import argparse
from ConfigParser import SafeConfigParser
from jsonpath import jsonpath
import sys
from ckanext.canada.metadata_schema import schema_description
class Converter:
    '''  
    This class is reponsible for taking JSON from NRCan and converting it into 
    Canada's CKAN json schema so it can be consumed by the server.
     
    It uses a mappings config file to figure out how to retrive 
    NRCan fiels and map them to their corresponding ckanext-canada fields  
         
    '''
        
    def __init__(self):
        pass
    def create_ckan_data(self):
       ''' Create NRCAN datasets in CKAN format and store in a text file '''
       config = SafeConfigParser()
       config.read('nrcan.config')
       infile = open('/Users/peder/dev/goc/nrcan.dat', "r")
       outfile = open('/Users/peder/dev/goc/nrcan-ckan.dat', "w")
       outfile = open('log.jl', "w")
       for line in infile:
           en,fr = str(line).strip().split('|')
           
           data_en= eval(en)
           print data_en['files']
           
           package_dict = {'extras': {}, 'resources': [], 'tags': []}
           
           # start with English Package Fields
           for ckan, nrcan in config.items('package'):
               if nrcan == "SELECT":
                  print "SELECT"
                  package_dict[ckan] = schema_description.dataset_field_by_id[ckan]['choices'][1]['key']
               elif "$." in nrcan:
                   print "Use JSON Path"
                   print nrcan
                   print jsonpath(data_en, nrcan)
               elif nrcan:
                   package_dict[ckan] = data_en[nrcan]
                   print data_en[nrcan]

           sys.exit()
           pass
       
if __name__ == "__main__":
    Converter().create_ckan_data()