'''
Created on 2013-01-10

@author: jakoped

This module is used for converting various items from in the pilot XML
'''
from ckanext.canada.metadata_schema import schema_description
from lxml import etree
from pprint import pprint
import mappings
import ckan_api_client
import sys
import random
"""

"""  
''' Pythonistic Strategy Pattern  :) '''
def map_name(code):
    ''' Combine statcan with id '''
    return 'statcan' + code.lower().split('-')[0]
    
def strategy_catalog_type():
    return  "strategically_named_catalog_type"
def strategy_dataset_link():
    return  "strategically_named_dataset_link"
def strategy_author():
    return  "Statistics Canada"

def map_subject(code):
    return "SUBJECT CODE "+ code

def map_geographic_region_name(code):
    return "GEOGRAPHIC REGION "+ code

def map_author(code):
    return  "stats-tab@statcan.gc.ca"

code_mapping_strategies = {'CD9CE9D4-1AA3-40DB-AF1F-37B392656033': map_subject,
                           '671506AE-ED00-4DAA-B856-895A6169BB60': map_author,
                           'C3A1CE57-4E0F-43AF-82A1-9C634AD8E292': map_geographic_region_name,
                           } 

default_strategies = {'catalog_type': strategy_catalog_type,
                      'url2':strategy_dataset_link,
                      'author':strategy_author} 

def convert_name(thisformid):
    
    name = thisformid.lower().split('-')[0]
    return "%s-%s" % ('statcan',name)
    



def process_record(node):
    package_dict = {'extras': {}, 'resources': [], 'tags': []}
    data = {}
    errors = {}
    extras ={}
    resource = {}
    resource_extras = {}
    resources = []
    
#    for f in schema_description.all_package_fields: print f
#    print "---"
#    for f in schema_description.all_resource_fields: print f
#    print "---"
#    for f in schema_description.extra_resource_fields: print f
#    print "---"
#    for f in schema_description.extra_package_fields: print f
#    sys.exit()
    
    for ckan_name, pilot_name, field in schema_description.dataset_all_fields():
        try: # the simplest case, one to one mapping of values
            # temporary hack because name has not been mapped to thisformid in the schema
            
            value = node.xpath("FORM[NAME='%s']/A/text()" % pilot_name)[0]
            pilot_code = value.split('|')
            if pilot_code[0] in code_mapping_strategies:
                data[ckan_name] = code_mapping_strategies[pilot_code[0]](pilot_code[1])
            else:
                data[ckan_name] = value

        except IndexError: #same as elif pilot_name is None:
            if ckan_name == "name": 
                data['name'] = "gen-" + str(round(random.random() * 10000000)).split('.')[0]
                print 
            elif ckan_name in default_strategies:
                data[ckan_name] = default_strategies[ckan_name]()

            else:
                data[ckan_name] = "default_" + ckan_name
     
        finally: 
            # reorganize dict for CKAN
            if ckan_name in schema_description.extra_package_fields:
               extras[ckan_name] = data[ckan_name]
               del data[ckan_name]  
            # now populate packages
            elif ckan_name == 'url':
                resource['url'] = "http://www.statcan.gc.ca/cgi-bin/sum-som/fl/cstsaveascsv.cgi?filename=arts63a-fra.htm&amp;lan=fre"
                #resource['url'] = node.xpath("FORM['dataset_link_en_1']/A/text()")[0]
            
            elif ckan_name in schema_description.all_resource_fields:
                resource[ckan_name] = "default_package_value " + ckan_name
                
                #if ckan_name != 'name': del data[ckan_name]
#            elif ckan_name in schema_description.all_resource_fields and ckan_name != 'name':  #FIXME
#                print "Resource gets " + ckan_name;
#                resource[ckan_name] = data[ckan_name];
#                del data[ckan_name]               
    
    resources.append(resource)         
    data['extras'] = extras
    data['resources'] = resources
    data['groups'] = ["statcan"]
   
#    extras = {key:value for (key, value) in data if key in schema_description.extra_package_fields}
    pprint(data)
    sys.exit()
    #ckan_api_client.insert(data)



def report(errors):
    print "Record Error: %s" % errors
   
def process_pilot_xml(xml_file):
    # by using the default 'end' event, you start at the _bottom_ of the tree
    for event, element in etree.iterparse(xml_file, events=("start","end")):
        if event == "start" and  element.tag == "record":
            process_record(element)
        element.clear()
        del element # for extra insurance  

              
if __name__ == "__main__":
    process_pilot_xml('data/tables_20120815.xml')

