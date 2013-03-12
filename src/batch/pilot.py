'''
Created on 2013-01-10

@author: jakoped

This module is used for converting various items from in the pilot XML
'''
from ckanext.canada.metadata_schema import schema_description
from lxml import etree
from pprint import pprint
import mappings
import random

import sys
import simplejson as json
import string

class PilotData():
    '''  Loads a large XML file and turns various useful generators '''
    def __init__(self,xml_file):
        pass
        self.xml_file = xml_file
    
    def _iter_open(self):
        # by using the default 'end' event, you start at the _bottom_ of the tree
        i = 0
        for event, element in etree.iterparse(self.xml_file, events=("start","end")):
            i += 1
            if event == "start" and  element.tag == "RECORD":
                yield element
            element.clear()
            del element # for extra insurance  
    def elements(self):   
        return self._iter_open()
            
class PilotReport:
    
    # create instance of PilotData
    data = PilotData("/Users/peder/dev/OpenData/Pilot/OpenData_Feb13_extract-1.xml");
    def number_of_records(self):
        counter = 0
        for x in self.data.elements():
            counter +=1
            print counter, "\r",
        print counter

        
class Transform:
    
    ''' A 3 pass method for turning pilot xml into CKAN json  
        each file takes a file and produces a new file.
    '''
    def structure(self):
        counter =0 
        ''' Step 1:  Create CKAN Structure  '''
        #self.out = open("/Users/peder/dev/OpenData/ckan-json/pilot-complete.jl", "w")
        for event, element in etree.iterparse("/Users/peder/dev/OpenData/Pilot/OpenData_Feb13_extract-1.xml", events=("start","end")):
            
            if event == "start" and  element.tag == "RECORD":
                counter+=1
                print counter
                #self._process_node(element)
                
            element.clear()
            del element # for extra insurance  
            
        #self.out.close()
        pass

    def _process_node(self,node):
        #print node.xpath("FORM[NAME='thisformid']/A/text()")
        #print etree.tostring(node, with_tail=True)
        
        package_dict = {'resources': [], 'tags':[]}
        
        for ckan_name, pilot_name, field in schema_description.dataset_all_fields():
            
            
            try: # the simplest case, one to one mapping of values
            # temporary hack because name has not been mapped to thisformid in the schema
                if ckan_name == "id":
                    #package_dict['id'] = node.xpath("FORM[NAME='thisformid']/A/text()")[0]
                    continue
                elif ckan_name == 'name':
                    package_dict['name'] = "pilot-" + str(node.xpath("FORM[NAME='thisformid']/A/text()")[0]).split("-")[0].lower()
                    continue
                elif ckan_name== 'tags':
                    continue
                else:
                    print ckan_name, pilot_name
                    value = node.xpath("FORM[NAME='%s']/A/text()" % pilot_name)[0]
                    

                if "|" in value:
                    split_value = value.split("|")[1]
                    rval = field['choices_by_pilot_uuid'][split_value]
                    package_dict[ckan_name] = rval['key']
                    
                    if pilot_name == "department":
                        print "ORGANIZATION " + str(rval['id']).lower()
                        package_dict['organization'] = str(rval['id']).lower()
                else:
                    package_dict[ckan_name] = value
            except IndexError:  #when None, eg. same as elif pilot_name is None:
               package_dict[ckan_name] = ''
               print "INDEX ERROR"
               pass
            except KeyError:
                print "KEY ERROR"
                
                pass
            
            # now do resources, use my own logic as 
            resources = []
            resource_dict = {}
            if ckan_name in schema_description.all_resource_fields:
                try:
                    value  = node.xpath("FORM[NAME='%s']/A/text()" % pilot_name)[0]
           
                    if "|" in value:
                        split_value = value.split("|")[1]
                        rval = field['choices_by_pilot_uuid'][split_value]
                        resource_dict[ckan_name] = rval['key']
                    else: 
                        resource_dict[ckan_name] = value
                        
                except IndexError:
                        continue
                    
                resources.append(resource_dict)
                package_dict['resources'] = resources 

        self.out.write(json.dumps(package_dict) + "\n")
        

def whatisthis(s):
    if isinstance(s, str):
        return "ordinary string"
    elif isinstance(s, unicode):
        return "unicode string"
    else:
        return "not a string"

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
    PilotReport().number_of_records();
    #Transform().structure()   
    #Transform().replace()
    #process_pilot_xml('data/tables_20120815.xml')

