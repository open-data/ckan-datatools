'''
Created on 2013-01-10

@author: jakoped

This module is used for converting various items from in the pilot XML
'''
#from ckanext.canada.metadata_schema import schema_description
from lxml import etree
from pprint import pprint
"""
The ELEMENT_LIST can be filled with something like if ckanext-canada is on the classpath
schema_set = set(ckan_id
            for ckan_id, ignore, field
            in schema_description.fields_by_ckan_id(include_existing=True)
            if field['existing'])
"""

import mappings
import ckan_api_client
import sys
     
def process_record(node):

    data = {}
    errors = {}
    
    try: 
        id = node.xpath("FORM[NAME='thisformid']/A/text()")[0]
    except IndexError: 
        pass

    for ckan_name,pilot_name in mappings.ckan_pilot_common:
        try:
            value = node.xpath("FORM[NAME='%s']/A/text()" % pilot_name)
            if pilot_name == 'department':
                data[ckan_name] = ["statcan"]
            else:
                data[ckan_name] = value[0]
                data['license'] = "Other (Open)"   
        except IndexError:
            errors[pilot_name] = 'Empty'
            pass
                  
        finally:
            pass
    # now do the same for resources
    resource = {}
    for ckan_name,pilot_name in mappings.common_resource_names:
        try:
            value = node.xpath("FORM[NAME='%s']/A/text()" % pilot_name)
        
            if pilot_name == "dataset_format_1":
                resource[ckan_name] = 'xls'
            else:    
                resource[ckan_name] = value[0]
        except IndexError:
            errors[pilot_name] = 'Empty' 
                              
    if errors:
        #report(errors)
        pass
    data['resources'] = [resource,]
    #pprint(convert(data))
    ckan_api_client.insert(convert(data))

x = 0
def convert(data):

    global x
    x+=1

    #print  x,data
    """eventually make the client api event driven"""   
    try:
 
        #Rules:  name must be alphanumeric
        #Name most be single word
        # name is a logical name aka URI in RDF
        #'name': [u'Url must be purely lowercase alphanumeric (ascii) characters and these symbols: -_']}"
        name = data['name'].lower()
        name = name.split('-')[0]
        data['name'] = "%s-%s" % (data['groups'][0],name)

    except KeyError:
        pass
    return data

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
    process_pilot_xml('tables_20120815.xml')

