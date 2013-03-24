'''
Created on 2013-01-10

@author: jakoped

This module is used for converting various items from in the pilot XML
'''
from ckanext.canada.metadata_schema import schema_description
from lxml import etree
from pprint import pprint
import random
from datetime import  datetime
import sys
import simplejson as json
import string
from common import XmlStreamReader
import logging
from guess_language import guess_language

# add filemode="w" to overwrite
logging.basicConfig(filename="/Users/peder/dev/goc/ckan-logs/pilot.log", level=logging.INFO)
pilot_file =  "/Users/peder/dev/OpenData/Pilot/OpenData_Feb13_extract-1.xml"     

class PilotXmlStreamReader(XmlStreamReader):
    ''' 
        Sometimes inheritance IS usuful ;)
        Combines stream of english and french records into one RECORD  
        because we are streaming, we cannot use:
        zip(data.elements()[0::2], data.elements()[1::2])
        TODO: Consider using fast_iter:
        http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
        FIXME: Need to skip every other one for this to work with i%2, 
        and can no longer clear element in parent
    '''
    def combined_elements(self):
        for i,element in enumerate(self._iter_open()):
            if element.getprevious() is not None:
                if i%2==0:continue
                yield (element.getprevious(),element)
            
            

class PilotReport:
    
    def __init__(self,datafile,report=False):
        # create instance of PilotData
        self.data = PilotXmlStreamReader("RECORD",datafile)

    def number_of_records(self):
        for i,nodes in enumerate(self.data.combined_elements()):
            (node,node_fr) = nodes
            #etree.dump(node, pretty_print=True)
            if i > 10: sys.exit()
            print "EN", node.xpath("DC.TITLE/text()")
            print "FR", node_fr.xpath("DC.TITLE/text()")
            print "---------------------"
            try:
                title, = nodes[0].xpath("DC.TITLE/text()")
                title_fr=  nodes[1].xpath("DC.TITLE/text()")
                #print i, title, title_fr
                #print i,title_en, title #guessLanguageName(title)
                if i > 10:
                    sys.exit()
            except Exception as e:
                print e
                #logging.error(e)
            #Replace with Logging framework. self.report.write(str(counter)+"\n")
        self.previous_node = node
        
    def unique_fields(self):
        counter = 0
        unique_form_id = 0        
        for doc in self.data.elements():
            
            self.report.write(str(counter)+"\n")    

        
class Transform:

    def _process_node(self,node):
        
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
    PilotReport(pilot_file).number_of_records()
    ''' 
    #PilotReport().number_of_records()
    #Transform().structure()   
    #Transform().replace()
    #process_pilot_xml('data/tables_20120815.xml')

    '''