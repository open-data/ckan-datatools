'''
Created on 2013-01-10

@author: jakoped

This module is used for converting various items from in the pilot XML
'''
#from ckanext.canada.metadata_schema import schema_description
from lxml import etree
from pprint import pprint

ELEMENT_LIST = ["uniqueformid","name","department","owner","title_en","contact_title"]

def process_record(node):

    data = {}
    errors = []
    # I only want this to happen if an assert is raised
    #errors['id'] = node.xpath("FORM[NAME='uniqueformid']/A/text()")
    id = node.xpath("FORM[NAME='uniqueformid']/A/text()")[0]
#    data['id'] = id;
    
    for name in ELEMENT_LIST:
        try:
            value = node.xpath("FORM[NAME='%s']/A/text()" % name)
            data[name] = value[0]
            
        except IndexError:
            #do some error stuff here
            errors.append({name,'empty'})
            pass
                  
        finally:
           pass
#    if errors:
#        error_report(id,errors)

    convert_logic(data)

def convert_logic(data):
#    pprint(data)
    
def error_report(id,errors):
    print "ERROR:"
    print id,errors
    #errors.append

def proces_record_old(node):
    ELEMENT_LIST = ["DC.TITLE","DEPARTMENT","URL"]
    for e in ELEMENT_LIST:
        if e == "DEPARTMENT":
            print 
        print "%s :: %s" % (e, node.findtext(e))
    print "---"
   
def process_pilot_xml(xml_file):
    # by using the default 'end' event, you start at the _bottom_ of the tree
    for event, element in etree.iterparse(xml_file, events=("start","end")):
        if event == "start" and  element.tag == "record":
            process_record(element)
        del element # for extra insurance  
    print "--------------"
              
if __name__ == "__main__":
    """
    schema_set = set(ckan_id
                for ckan_id, ignore, field
                in schema_description.fields_by_ckan_id(include_existing=True)
                if field['existing'])
    """
    #pprint(schema_set)
    process_pilot_xml('pilot.xml')
