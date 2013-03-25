'''
Created on 2013-01-10

@author: jakoped

This module is used for converting various items from in the pilot XML
'''
import sys
import logging
import simplejson as json
from lxml import etree
from pprint import pprint
from datetime import  datetime
from common import XmlStreamReader
from guess_language import guess_language
from ckanext.canada.metadata_schema import schema_description

# add filemode="w" to overwrite
logging.basicConfig(filename="/Users/peder/dev/goc/ckan-logs/pilot.log", level=logging.INFO)
pilot_file =  "/Users/peder/dev/OpenData/Pilot/OpenData_Feb13_extract-1.xml" 
pilot_file =  "/Users/peder/dev/OpenData/Pilot/OpenData_Feb13_extract-1.xml" 
output_file =  "/Users/peder/dev/OpenData/Pilot/march_25.jl"

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
            if i > 50: sys.exit()
            print "EN", node.xpath("DC.TITLE/text()")
            print "FR", node_fr.xpath("DC.TITLE/text()")
            print "---------------------"
            try:
                title, = nodes[0].xpath("DC.TITLE/text()")
                title_fr=  nodes[1].xpath("DC.TITLE/text()")
                #print i, title, title_fr
                #print i,title_en, title #guessLanguageName(title)
                if i > 50:
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


formats = schema_description.resource_field_by_id['format']['choices_by_pilot_uuid']

class Transform:
    
    def __init__(self,datafile,outfile):
        
        self.outfile = open(outfile,"w")
        self.data = PilotXmlStreamReader("RECORD",datafile)
        
    def write_jl_file(self):
        for i,nodes in enumerate(self.data.combined_elements()):
            print i
            (node,node_fr) = nodes
            self._process_node(node,node_fr)
            

    def _process_node(self,node,node_fr):

        package_dict = {'resources': [], 'tags':[]}

        # Resource fields are not mapped in schema, so do them first 
        dataset_links=['dataset_link_en_%d' % n for n in range(1,7)]
 
        for i, dl in enumerate(dataset_links):

            try:
                link = node.xpath("FORM[NAME='%s']/A/text()" % dl)[0]
                format_code = node.xpath("FORM[NAME='%s']/A/text()" % "dataset_format_%d" % (i+1))[0].split("|")[1]
                format = formats[format_code]['key']
                link_fr = node_fr.xpath("FORM[NAME='%s']/A/text()" % dl)[0]
                resource_dict = {'url':link, 'format':format } 
                resource_dict_fr = {'url':link_fr, 'format':format } 
                package_dict['resources'].append(resource_dict)
                if link_fr != link:
                    package_dict['resources'].append(resource_dict_fr)
            except IndexError as e:
                print "RESOURCE ERROR ", e
   
            except Error as e:
                print e
    
                        
        for ckan_name, pilot_name, field in schema_description.dataset_all_fields():
            try:
                     
                if ckan_name == "id":
                    continue
                elif ckan_name in dataset_links:
                    continue
                elif ckan_name == 'name':
                    #package_dict['name'] = "pilot-" + str(node.xpath("FORM[NAME='thisformid']/A/text()")[0]).split("-")[0].lower()
                    #Makus request it be just the id
                    package_dict['name'] = "pilot-" + str(node.xpath("FORM[NAME='thisformid']/A/text()")[0]).lower() 
                    continue
                elif ckan_name== 'tags':
                    continue
                else:
                    value = node.xpath("FORM[NAME='%s']/A/text()" % pilot_name)[0]
                    
                if "|" in value:
                    split_value = value.split("|")[1]
                    rval = field['choices_by_pilot_uuid'][split_value]
                    package_dict[ckan_name] = rval['key']
                    
                    if pilot_name == "department":
                        package_dict['organization'] = str(rval['id']).lower()
                else:
                    package_dict[ckan_name] = value
            except IndexError:  #when None, eg. same as elif pilot_name is None:
               package_dict[ckan_name] = ''
               print "INDEX ERROR ", ckan_name, pilot_name
               pass
            except KeyError:
                print "KEY ERROR" 
                pass
            except Error as e:
                print e
        
        self.outfile.write(json.dumps(package_dict) + "\n")
           
if __name__ == "__main__":
    #PilotReport(pilot_file).number_of_records()
    Transform(pilot_file,output_file).write_jl_file()
    ''' 
    #PilotReport().number_of_records()
    #Transform().structure()   
    #Transform().replace()
    #process_pilot_xml('data/tables_20120815.xml')

    '''