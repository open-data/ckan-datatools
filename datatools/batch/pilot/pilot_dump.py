#-*- coding:UTF-8 -*-
import os
import sys
from lxml import etree
from pprint import pprint
from string import Template
from datatools.batch.common import XPather
from datatools.batch import common
from ckanext.canada.metadata_schema import schema_description as schema
from pilot_model import PilotRecord

''' 
    RESOURCE:
        1 name
        2 name_fra
        3 resource_type
        4 url
        5 size
        6 format
        7 language
    DATASET:
        1 id
        2 owner_org
        3 title
        4 title_fra
        5 notes
        6 notes_fra
        7 catalog_type
        8 subject
        9 topic_category
        10 keywords
        11 keywords_fra
        12 license_id
        13 geographic_region
        14 spatial
        15 spatial_representation_type
        16 presentation_form
        17 browse_graphic_url
        18 date_published
        19 date_modified
        20 maintenance_and_update_frequency
        21 data_series_name
        22 data_series_name_fra
        23 data_series_issue_identification
        24 data_series_issue_identification_fra
        25 digital_object_identifier
        26 time_period_coverage_start
        27 time_period_coverage_end
        28 url
        29 url_fra
        30 endpoint_url
        31 endpoint_url_fra
        32 ready_to_publish
        33 portal_release_date
        '''


package_dict = {'resources': []}  

def resources():

    resources = []
    path = '//gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine'
    online=doc.xpath(path,namespaces=nspace)
    for node in online:
        
        try:
            resource_dict={}
            resource_dict['url'] = node.find('gmd:CI_OnlineResource/gmd:linkage/gmd:URL', nspace).text
            resource_dict['language']=doc.find('//gmd:MD_DataIdentification/gmd:language/gco:CharacterString', nspace).text
            resource_dict['name']=node.find('gmd:CI_OnlineResource/gmd:description/gco:CharacterString', nspace).text
            resource_dict['name_fra']=node.find('gmd:CI_OnlineResource/gmd:description/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString', nspace).text
            resource_dict['size']=doc.find('//gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:transferSize/gco:Real', nspace).text
            #protocol = node.find('gmd:CI_OnlineResource/gmd:protocol/gco:CharacterString',nspace).text
            format = doc.find('//gmd:distributionInfo/gmd:MD_Distribution/gmd:distributionFormat/gmd:MD_Format/gmd:name/gco:CharacterString',nspace).text
            
            if format not in formatTypes:
     
                resource_dict['format'] = formatTypes['Other']
            else:
                resource_dict['format'] = formatTypes[format]

            resources.append(resource_dict)
        except:
            raise
   

def data_identification():
    #8 of 33
    package_dict['id'] ='MISSING' #charstring_path('fileIdentifier')
    #package_dict['language']=schema.dataset_field_by_id['language']['example']['eng']
    package_dict['owner_org']='nrcan-rncan'          
    package_dict['topic_category']=full_path('//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:topicCategory/gmd:MD_TopicCategoryCode')
    package_dict['subject']=get_subject_from_topic_category(package_dict['topic_category']) 
    package_dict['catalog_type']=u"Geo Data | G\xe9o"
    package_dict['license_id']="ca-ogl-lgo"
    package_dict['presentation_form']=get_presentation_code()
    package_dict['browse_graphic_url']='MISSING'
    package_dict['digital_object_identifier']='MISSING'

def time_and_space():
    #10 if 33
    package_dict['date_published']=full_path('//gmd:CI_Date/gmd:date/gco:Date')
    package_dict['date_modified']='MISSING'
    package_dict['maintenance_and_update_frequency']=get_update_frequency()
    package_dict['portal_release_date']='2013-05-24'
    package_dict['ready_to_publish']=True
    start,end = get_time()
    package_dict['time_period_coverage_start']=start
    package_dict['time_period_coverage_end']=end
    package_dict['geographic_region']='MISSING'
    package_dict['spatial']=get_spatial()
    package_dict['spatial_representation_type']=get_spatial_rep_type()

def bilingual():
    #14 of 33
    package_dict['data_series_name']=full_path('//gmd:CI_Citation/gmd:series/gmd:CI_Series/gmd:name/gco:CharacterString')
    package_dict['data_series_name_fra']=full_path('//gmd:CI_Citation/gmd:series/gmd:CI_Series/gmd:name/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString')
    package_dict['data_series_issue_identification']=full_path('//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:series/gmd:CI_Series/gmd:issueIdentification/gco:CharacterString')
    package_dict['data_series_issue_identification_fra']=package_dict['data_series_issue_identification']
    #package_dict['endpoint_url']='http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/'
    #package_dict['endpoint_url_fra']='http://geogratis.gc.ca/api/fr/nrcan-rncan/ess-sst/'
    package_dict['url']='http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/'
    package_dict['url_fra']='http://geogratis.gc.ca/api/fr/nrcan-rncan/ess-sst/'
    package_dict['keywords']=get_keywords('//gmd:keyword/gco:CharacterString')
    package_dict['keywords_fra']=get_keywords('//gmd:keyword/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString')
    package_dict['notes']=get_notes('//gmd:abstract/gco:CharacterString')
    package_dict['notes_fra'] =get_notes('//gmd:abstract/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString') 
    package_dict['title'] = full_path('//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString')
    package_dict['title_fra'] = full_path('//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString')

def check_structure(dict):
    fields =  [ckan for ckan,pilot,field in schema.dataset_all_fields() if field['type'] not in [u'fixed',u'calculated']] 
    mandatory = [ckan for ckan,pilot,field in schema.dataset_all_fields() if field['mandatory'] == u'all']  
    fields.append('resources')  
    fields.append('validation_override')     
    missing_fields = set(dict.iterkeys()).symmetric_difference(set(fields)) 
    
    mandatory_fields = set(mandatory).intersection(set(fields))
    print "Missing Mandatory Fields", missing_fields.intersection(mandatory_fields)
    

    print "Missing Values ", [key for key,value in dict.items() if value=='MISSING']
    print "------------- Details ---------------"
    print "Fields Missing from Package_dict"
    pprint(list(missing_fields))
    
    print "Mandatory Fields that are not fixed or calculated"
    pprint(mandatory_fields)
   
    

 
            
def process(file): 
    tree = etree.parse(file)
    root = tree.getroot()
    records=[]
        
    for i,node in enumerate(root):
   
        id = str(node.xpath("FORM[NAME='thisformid']/A/text()")[0]).lower() 

        record = PilotRecord(node)
        records.append(record)
  
         
        
            #data_identification()
#            time_and_space()
#            bilingual()
#            resources()
#            package_dict['validation_override']=False 
#            check_structure(package_dict)
#            pprint(package_dict)
#            
#            sys.exit()
#            if (n % 100) == 0: print n 
#
#            #jlfile.write(json.dumps(package_dict) + "\n")  

    for record in records:
        print record.id
        print record.display(raw=True)
        print "--------------------------------------------------"
        sys.exit()
        
if __name__ == "__main__":
    matched_file =  "/Users/peder/dev/goc/LOAD/pilot-matched.xml"
    bilingual_file =  "/Users/peder/dev/goc/LOAD/pilot-bilingual.xml"
    
    process(bilingual_file)
    #process()