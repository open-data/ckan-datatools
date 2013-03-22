'''
Created on 2013-01-10

@author: jakoped

This module is used for converting various items from in the pilot XML
'''
from ckanext.canada.metadata_schema import schema_description
from lxml import etree
from pprint import pprint
import random

import sys
import simplejson as json
import string

class PilotXmlReader():
    '''  Loads a large XML file and turns various useful generators '''
    def __init__(self,xml_file):
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
    data = PilotXmlReader("/Users/peder/dev/OpenData/Pilot/OpenData_Feb13_extract-1.xml");
    report = open("/Users/peder/dev/OpenData/Pilot/pilot-report.txt", "a")
    
    def number_of_records(self):
        counter = 0
        for doc in self.data.elements():
            counter +=1
            self.report.write(str(counter)+"\n")
    
    def unique_fields(self):
        counter = 0
        unique_form_id = 0
        
        for doc in self.data.elements():
            
            self.report.write(str(counter)+"\n")    

        
class Transform:

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

           
if __name__ == "__main__":
 
    ''' 
    #PilotReport().number_of_records();
    #Transform().structure()   
    #Transform().replace()
    #process_pilot_xml('data/tables_20120815.xml')

    '''