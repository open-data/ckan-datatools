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
from datetime import date
import common
from common import XmlStreamReader
from ckanext.canada.metadata_schema import schema_description

# add filemode="w" to overwrite
logging.basicConfig(filename="/Users/peder/dev/goc/ckan-logs/pilot.log", level=logging.INFO)
pilot_file =  "/Users/peder/dev/OpenData/Pilot/OpenData_Feb13_extract-1.xml"  
output_file =  "/Users/peder/dev/OpenData/Pilot/april_15.jl"

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
                     
formats = schema_description.resource_field_by_id['format']['choices_by_pilot_uuid']

class Transform:
    
    def __init__(self,datafile,outfile):
        
        self.outfile = open(outfile,"w")
        self.data = PilotXmlStreamReader("RECORD",datafile)
        
    def write_jl_file(self):
        for i,nodes in enumerate(self.data.combined_elements()):
            
            (node,node_fr) = nodes
            self._process_node(i,node,node_fr)
    def strip_title(self, title):
        language_markers = common.title_langauge_markers + common.title_langauge_markers_fra        
   
        for marker in language_markers:
            if marker in title:
                return title.replace(marker, '')
            
    def _process_node(self,count, node,node_fr):
        package_dict = {'resources': [], 'tags':[]}

        # Resource fields are not mapped in schema, so do them first 
        dataset_links=['dataset_link_en_%d' % n for n in range(1,7)]
 
        for i, dl in enumerate(dataset_links):
           
            try:
                link = node.xpath("FORM[NAME='%s']/A/text()" % dl)[0]
                format_code = node.xpath("FORM[NAME='%s']/A/text()" % "dataset_format_%d" % (i+1))[0].split("|")[1]
                format = formats[format_code]['key']
                
                link_fr = node_fr.xpath("FORM[NAME='%s']/A/text()" % dl)[0]
                resource_dict = {'url':link, 'format':format, 'resource_type': 'Dataset','language':'English | Anglais'} 
                resource_dict_fr = {'url':link_fr, 'format':format, 'resource_type': 'Dataset','language':'French | Fran\u00e7ais'} 
                package_dict['resources'].append(resource_dict)
                if link_fr != link:
                    package_dict['resources'].append(resource_dict_fr)
            except IndexError as e:
                #print "RESOURCE ERROR ", e, link
                #This simply means that there is an empty link element, and it should be ignored
                pass
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
                    package_dict['name'] =  str(node.xpath("FORM[NAME='thisformid']/A/text()")[0]).lower() 
                    continue
                elif ckan_name== 'tags':
                    continue
                elif ckan_name == 'title':
                    package_dict['title'] =  self.strip_title(node.xpath("FORM[NAME='title_en']/A/text()")[0])
                elif ckan_name=='title_fra':
                    package_dict['title_fra'] =  self.strip_title(node.xpath("FORM[NAME='title_fr']/A/text()")[0])
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
               #print "INDEX ERROR ", ckan_name, pilot_name
               pass
            except KeyError as e:
                print "KEY ERROR : ", pilot_name, e 
                

        # Filter out things that will not pass validatation
        if package_dict['geographic_region'] == "Canada  Canada":package_dict['geographic_region']=''
        package_dict['author_email'] =  'open-ouvert@tbs-sct.gc.ca'  
        package_dict['catalog_type'] = schema_description.dataset_field_by_id['catalog_type']['choices'][0]['key']
        package_dict['resource_type'] = 'file' #schema_description.dataset_field_by_id['resource_type']['choices']['file']
        print package_dict['url']
        print package_dict['url_fra']
            
#        print "-------------{}----------".format(count)
#        print package_dict['title']
#        print package_dict['title_fra']
#        pprint(package_dict['resources'])
 
        #self.outfile.write(json.dumps(package_dict) + "\n")
           
if __name__ == "__main__":

    #PilotReport(pilot_file).number_of_records()
    outputdir = '/Users/peder/dev/goc/LOAD'
    pilot_file =  "/Users/peder/dev/goc/OD_DatasetDump-0.xml" 
    output_file =  "{}/pilot-{}.jl".format(outputdir,date.today()) 
    Transform(pilot_file,output_file).write_jl_file()

    #Transform().structure()   
    #Transform().replace()
    #process_pilot_xml('data/tables_20120815.xml')
