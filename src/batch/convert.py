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
            if pilot_code[0] in mappings.code_mapping_strategies:
                data[ckan_name] = mappings.code_mapping_strategies[pilot_code[0]](pilot_code[1])
            else:
                data[ckan_name] = value

        except IndexError: #same as elif pilot_name is None:
            if ckan_name == "name": 
                data['name'] = "gen-" + mappings.random_id()
                print 
            elif ckan_name in mappings.default_strategies:
                data[ckan_name] = mappings.default_strategies[ckan_name]()

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

