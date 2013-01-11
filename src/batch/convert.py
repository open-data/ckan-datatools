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
ELEMENT_LIST = ["uniqueformid","name","department","owner","title_en"]

def process_record(node):

    data = {}
    errors = {}
    id = node.xpath("FORM[NAME='uniqueformid']/A/text()")[0]
 
    for name in ELEMENT_LIST:
        try:
            value = node.xpath("FORM[NAME='%s']/A/text()" % name)
            data[name] = value[0]
            
        except IndexError:
            errors[name] = 'Empty'
            pass
                  
        finally:
           pass
    if errors:
        errors['id'] = id
        report(errors)

    convert_logic(data)

def convert_logic(data):
#    pprint(data)
#    mappings = {''}
    ### this neeed some If IN logic + put in a config file
    if data['department'] == '671506AE-ED00-4DAA-B856-895A6169BB60|A0F0FCFC-BC3B-4696-8B6D-E7E411D55BAC':
        data['department'] = 'statcan'
    pprint(data)
      
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
    process_pilot_xml('pilot.xml')
