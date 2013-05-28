#-*- coding:UTF-8 -*-
import os
import sys
from lxml import etree
from pprint import pprint
from string import Template
from datatools.batch.common import XPather
from datatools.batch import common
from ckanext.canada.metadata_schema import schema_description as schema


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
        2 language
        3 owner_org
        4 author_email
        5 title
        6 title_fra
        7 name
        8 notes
        9 notes_fra
        10 catalog_type
        11 subject
        12 topic_category
        13 keywords
        14 keywords_fra
        15 license_id
        16 attribution
        17 attribution_fra
        18 geographic_region
        19 spatial
        20 spatial_representation_type
        21 presentation_form
        22 browse_graphic_url
        23 date_published
        24 date_modified
        25 maintenance_and_update_frequency
        26 data_series_name
        27 data_series_name_fra
        28 data_series_issue_identification
        29 data_series_issue_identification_fra
        30 digital_object_identifier
        31 time_period_coverage_start
        32 time_period_coverage_end
        33 url
        34 url_fra
        35 endpoint_url
        36 endpoint_url_fra
        37 ready_to_publish
        38 portal_release_date
'''

nspace = common.nap_namespaces
presentationCodes = dict((choice['id'],choice['key']) for choice in schema.dataset_field_by_id['presentation_form']['choices'])
spatialRepTypeCodes = dict((choice['id'],choice['key']) for choice in schema.dataset_field_by_id['spatial_representation_type']['choices'])
maintenanceFrequencyCodes = dict((item['id'], item['key']) for item in schema.dataset_field_by_id['maintenance_and_update_frequency']['choices'])
topicKeys = dict((item['eng'], item['key']) for item in schema.dataset_field_by_id['topic_category']['choices'])
formatTypes=dict((item['eng'], item['key']) for item in schema.resource_field_by_id['format']['choices'])
pprint(formatTypes)

doc=None

def georegions():
    #  replace with list comprehension
    # this should be similar to minx, miny, maxx, maxy
    boundingBox = ['westBoundLongitude','southBoundLatitude','eastBoundLongitude','northBoundLatitude']
    regions = []
    for line in boundingBox:
        
        regions.append(doc.xpath('//gmd:%s/gco:Decimal' % line,namespaces=nspace)[0].text)
        
    return regions

def get_spatial():
    exteriorRing = doc.xpath('//gml:Polygon/gml:exterior/gml:LinearRing/gml:pos',namespaces=nspace)   
    interiorRing = doc.xpath('//gml:Polygon/gml:interior/gml:LinearRing/gml:pos',namespaces=nspace)   
    extent_template = Template('''{"type": "Polygon", "coordinates": [[[$minx, $miny], [$minx, $maxy], [$maxx, $maxy], [$maxx, $miny], [$minx, $miny]]]}''')

    extRingPoints = [map(float,p.text.split()) for p in  exteriorRing]
    
   
    intRingPoints = [p.text.split(" ") for p in interiorRing]
    if extRingPoints:
        return  geojson.dumps(geojson.geometry.Polygon([extRingPoints]))    
                              
    else: 
        return extent_template.substitute(
                                minx = georegions()[0],
                                miny = georegions()[1],
                                maxx = georegions()[2],
                                maxy = georegions()[3]
                                )
def get_spatial_rep_type():
    try:
        pCode = doc.xpath('//gmd:MD_SpatialRepresentationTypeCode',namespaces=nspace)[0].attrib['codeListValue'].split("_")[1]
        return spatialRepTypeCodes[int(pCode)]
    except IndexError:
        return ''
    except KeyError:
        print "Spatial Rep Type not in Schema", int(pCode)
    except:
        raise
def get_keywords(path):
    keywords = doc.xpath(path,namespaces=nspace)
    def clean_tag(x):
        #replace forward slashes and semicolon so keywords will pass validation
        #Apostrophes in french words causes a proble; temporary fixx
        x = x.replace("/"," - ").replace("; ","-")
        return x.split(">")[-1].lower().strip().capitalize() 
         
    tags = [clean_tag(t.text) for t in keywords]  # must remove forward slashes to pass validation          
    return ",".join(tags)

def get_time():
    time = doc.xpath('//gml:begin/gml:TimeInstant/gml:timePosition',namespaces=nspace)
    #end = doc.xpath('/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:begin/gml:TimeInstant/gml:timePosition',namespaces=nspace)

    try:         
        t = common.time_coverage_fix(time[0].text,time[1].text)
        return (common.timefix(t[0]),common.timefix(t[1]))

    except IndexError, ValueError:
        return ("","")
    
def get_presentation_code():
    try:
        pCode = doc.xpath('//gmd:CI_PresentationFormCode',namespaces=nspace)[0].attrib['codeListValue'].split("_")[1]
        pName = presentationCodes[int(pCode)]
        return pName
    except IndexError:
        print "No presentation Form"
        return presentationCodes[387]
    except KeyError:
        print "Presentation code not in Schema"
        return ''
 
def get_notes(path):
    try:
        notes = doc.xpath(path,namespaces=nspace)[0].text
        if 'Abstract not available' in notes:
            notes="Abstract not available."
        if 'Résumé non disponible' in notes:
            notes=u"Résumé non disponible."
        return notes
    except:
        raise

def get_update_frequency():
    try:
        frequencyCode = doc.xpath('//gmd:MD_MaintenanceFrequencyCode',namespaces=nspace)[0].attrib['codeListValue'].split("_")[1]
        return maintenanceFrequencyCodes[frequencyCode]

    except KeyError:
        return "As Needed | Au besoin"

  
def full_path(path):
    return doc.xpath((path),namespaces=nspace)[0].text

def charstring_path(key):
    return doc.xpath(('//gmd:%s/gco:CharacterString' % key),namespaces=nspace)[0].text
                

package_dict = {'resources': [], 'tags':[]}  

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
            resource_dict['format'] = doc.find('//gmd:distributionInfo/gmd:MD_Distribution/gmd:distributionFormat/gmd:MD_Format/gmd:name/gco:CharacterString',nspace).text
            #format_fra=doc.find('//gmd:distributionInfo/gmd:MD_Distribution/gmd:distributionFormat/gmd:MD_Format/gmd:name/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString',nspace).text
            

            
#            if format not in formatTypes:
#                continue
#            else:
#                pass
                #resource_dict['format'] = formatTypes[format]
                
                    
            #MISSING resource_dict['name_fra']
            resources.append(resource_dict)
        except:
            raise
        
        package_dict['resources']= resources
        

        
        
        
        

def data_identification():
    #12 of 45
    package_dict['id'] = charstring_path('fileIdentifier')
    package_dict['language']=schema.dataset_field_by_id['language']['example']['eng']
    package_dict['owner_org']='nrcan-rncan'
    package_dict['author_email']=charstring_path('electronicMailAddress')             
    #package_dict['name']   type: calculated
    package_dict['catalog_type']=u"Geo Data | G\xe9o"
    #package_dict['subject']  only used in pilot
    #MISSING package_dict['topic_category']  #//gmd:MD_TopicCategoryCode is missing from the new XML format
    package_dict['license_id']="ca-ogl-lgo"
    package_dict['presentation_form']=get_presentation_code()
    #MISSING package_dict['browse_graphic_url']
    #NOT REQUIRED package_dict['digital_object_identifier']=''

def time_and_space():
    #11 of 45
    package_dict['date_published']=full_path('//gmd:CI_Date/gmd:date/gco:Date')
    #MISSING OR NOT REQUIRED package_dict['date_modified']
    package_dict['maintenance_and_update_frequency']=get_update_frequency()
    package_dict['validation_override']=True  
    package_dict['portal_release_date']='2013-05-24'
    package_dict['ready_to_publish']=True
    start,end = get_time()
    package_dict['time_period_coverage_start']=start
    package_dict['time_period_coverage_end']=end
    package_dict['geographic_region']=''
    package_dict['spatial']=get_spatial()
    package_dict['spatial_representation_type']=get_spatial_rep_type()

def bilingual():
    # 14 of 45
    #package_dict['attribution']  Generated by ckanext-canada
    #package_dict['attribution_fr'] Generated by ckanext-canada
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
                    
def process(dir): 
    global doc
    for (path, dirs, files) in os.walk(os.path.normpath(dir)):
        for n,file in enumerate(files):
            
            f = open(os.path.join(path,file),"r")
            doc = etree.parse(f)
            data_identification()
            time_and_space()
            bilingual()
            resources()
            pprint(package_dict)
            sys.exit()
            if (n % 100) == 0: print n 

            #jlfile.write(json.dumps(package_dict) + "\n")  


if __name__ == "__main__":
    dir="/Users/peder/dev/OpenData/nrcandump-sample"
    process(dir)
    #process()