import json
from pprint import pprint 
import argparse
from ConfigParser import SafeConfigParser
from jsonpath import jsonpath
import sys
from ckanext.canada.metadata_schema import schema_description


class Converter:
    config = SafeConfigParser()

class NrCan(Converter):
    '''  
    This class is reponsible for taking JSON from NRCan and converting it into 
    Canada's CKAN json schema so it can be consumed by the server.
     
    It uses a mappings config file to figure out how to retrive 
    NRCan fiels and map them to their corresponding ckanext-canada fields  
         
    '''
        
    def __init__(self):
        pass
    def get_choice_for_english_value(self,name,value):
        ''' Returns the English | French value from the metadata schema '''
        # Tuple unpacking  a one element tuple , and will explicitly cause helpful error message if it's not the right lenghe
        '''
        
        '''
        (rval,) = [c['key'] for c in schema_description.dataset_field_by_id[name]['choices'] if c['eng'] == value]
        return rval
                     
    def create_ckan_data(self):
       ''' Create NRCAN datasets in CKAN format and store in a text file '''
       self.config.read('nrcan.config')
       infile = open('/Users/peder/dev/goc/nrcan.dat', "r")
       outfile = open('/Users/peder/dev/goc/nrcan-ckan.dat', "w")
       outfile = open('log.jl', "w")
       for line in infile:
           en,fr = str(line).strip().split('|')    
           data_en= eval(en)
           package_dict = {'extras': {}, 'resources': [], 'tags': []}

           # start with English Package Fields
           lookups =[]
           for ckan, nrcan in config.items('package'):
               if nrcan=='LOOKUP':
                  lookups.append(ckan)
               elif "$." in nrcan:
                   print jsonpath(data_en, nrcan)
                   if schema_description.dataset_field_by_id[ckan].get('type') == 'keywords':
                       package_dict[ckan] = ','.join(jsonpath(data_en, nrcan))
                   else:
                       (package_dict[ckan],) = jsonpath(data_en, nrcan)
               elif nrcan:
                   package_dict[ckan] = data_en[nrcan]
                   
                   
               # After both languages are done, we can deal with lookups.    
               for ckan in lookups:
                  if ckan == 'catalog_type':
                       package_dict[ckan] = self.get_choice_for_english_value(ckan,'Geo Data')

                  elif ckan =='maintenance_and_update_frequency':
                      package_dict[ckan] = self.get_choice_for_english_value(ckan,'Unknown')
                
                  elif ckan =='maintenance_and_update_frequency':
                      package_dict[ckan] = self.get_choice_for_english_value(ckan,'Unknown')
        
           
           pprint(package_dict)
           sys.exit()
           pass
       
class Pilot(Converter):
    pass

    def __init__(self):
        self.config.read('pilot.config')
    
    def transform(self):
        infile = open('/Users/peder/dev/goc/nrcan.dat', "r")
        outfile = open('/Users/peder/dev/goc/pilot-ckan.dat', "w")

if __name__ == "__main__":
    Converter().create_ckan_data()