#-*- coding:UTF-8 -*-
import os
import sys
import json
import geojson
from lxml import etree
from pprint import pprint
from string import Template
from datatools.batch.common import XPather
from datetime import date,datetime
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

nspace = common.nap_namespaces
presentationCodes = dict((choice['id'],choice['key']) for choice in schema.dataset_field_by_id['presentation_form']['choices'])
spatialRepTypeCodes = dict((choice['id'],choice['key']) for choice in schema.dataset_field_by_id['spatial_representation_type']['choices'])
maintenanceFrequencyCodes = dict((item['id'], item['key']) for item in schema.dataset_field_by_id['maintenance_and_update_frequency']['choices'])
topicKeys = dict((item['eng'], item['key']) for item in schema.dataset_field_by_id['topic_category']['choices'])
formatTypes=dict((item['eng'], item['key']) for item in schema.resource_field_by_id['format']['choices'])
geographic_regions=dict((region['eng'],region['key']) for region in schema.dataset_field_by_id['geographic_region']['choices'])

formatTypes['GeoTIFF (Georeferenced Tag Image File Format)']='tiff'
formatTypes['TIFF (Tag Image File Format)']="tiff"
formatTypes['GeoTIFF']='tiff'
formatTypes['Adobe PDF']='PDF'
formatTypes['PDF - Portable Document Format']="PDF"    
formatTypes['ASCII (American Standard Code for Information Interchange)']="TXT"
formatTypes['GML (Geography Markup Language)']="gml"
formatTypes['Shape']="SHAPE"
formatTypes['gzip (GNU zip)']="ZIP"
formatTypes['ZIP']="ZIP"
formatTypes['ESRI Shapefile']="SHAPE"
formatTypes['JPEG']="jpg"
#Hierarchical Data Format (HDF)
#CorelDraw


geographic_regions['Yukon Territory']="Yukon  Youkon"
geographic_regions['Yukon']="Yukon  Youkon"
geographic_regions['Canada']=''



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
 
    extRingPoints = [map(float,reversed(p.text.split())) for p in  exteriorRing]

   
    intRingPoints = [p.text.split(" ") for p in interiorRing]
    if intRingPoints:print "INTERIOR", intRingPoints
    
    
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
        if x:
            x = x.replace("/"," - ").replace("; ","-")
            return x.split(">")[-1].strip()
        
         
    tags = [clean_tag(t.text) for t in keywords if len(t)>0]  # must remove forward slashes to pass validation          
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
        if u'Résumé non disponible' in notes:
            notes=u"Résumé non disponible."
        return notes
    except:
        raise
def camel_to_label(ccname):
    """
    Convert a camelcase name with irregularities from our proposed xml file
    to a field label with spaces

    >>> camel_to_label(u'relatedDocumentsURL')
    u'Related Documents URL'
    >>> camel_to_label(u'URLdocumentsConnexes')
    u'URL Documents Connexes'
    >>> camel_to_label(u'URIJeuDonn�es')
    u'URI Jue Donn�es'
    """
    
    special = (u'URL', u'URI')
    for s in special:
        if s in ccname:
            return (u' '+s+u' ').join(
                camel_to_label(w) for w in ccname.split(s)).strip()
    out = list(ccname[:1])
    for a, b in zip(ccname, ccname[1:]):
        if a.islower() and b.isupper():
            out.append(u' ')
        out.append(b)
    return u''.join(out).title()

def get_topic_category():
     topic_category_code = full_path('//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:topicCategory/gmd:MD_TopicCategoryCode')
     topic_name_en = camel_to_label(topic_category_code)
     try:
         topic = topicKeys[topic_name_en]
     except KeyError:
         topic =''
     
     return topic
     
def get_subject_from_topic_category():
    topic_category_code = full_path('//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:topicCategory/gmd:MD_TopicCategoryCode')

    subjects=[]
    topic_name_en = camel_to_label(topic_category_code)

   
    try:
         topic = topicKeys[topic_name_en]
    except KeyError:
         topic =''

    try:
       
        subject_ids = schema.dataset_field_by_id['topic_category']['choices_by_key'][topic]['subject_ids']
        for subject_id in subject_ids:
            subjects.append(schema.dataset_field_by_id['subject']['choices_by_id'][subject_id]['key'])
        result= ", ".join(set(subjects))
        return result
   
        
    except KeyError as e:
        return ''
    
    except:
        raise

def get_doi():  
    doi =  doc.xpath('//gmd:otherCitationDetails/gco:CharacterString',namespaces=nspace)
    if doi:
        return doi[0].text.split("doi ")[1]
    else:
        return ''

def get_update_frequency():
    try:
        frequencyCode = doc.xpath('//gmd:MD_MaintenanceFrequencyCode',namespaces=nspace)[0].attrib['codeListValue'].split("_")[1]
        return maintenanceFrequencyCodes[int(frequencyCode)]

    except IndexError,KeyError:
        return "As Needed | Au besoin"

  
def full_path(path):
    try:
        return doc.xpath((path),namespaces=nspace)[0].text
    except:
        return ''

def charstring_path(key):
    return doc.xpath(('//gmd:%s/gco:CharacterString' % key),namespaces=nspace)[0].text
                
def keywords_by_code(doc,code_value,nspace):
    ''' pass xml and code value, get back a list of keywords  '''
    keywords = []
    elems = doc.xpath('//gmd:MD_KeywordTypeCode[@codeListValue="%s"]/../../gmd:keyword/gco:CharacterString' % code_value,namespaces=nspace)
    try:
        for e in elems:
            if " > " in e.text: 
                keywords.append(e.text.split(" > ")[-1].title())
            elif re.match("^[A-Z0-9]", e.text): #^[A-Z0-9]{3}(?:List)?$
                pass
            else:
                keywords.append(e.text)
        if len(elems) == 0:  
            raise EmptyKeyword 
    except Exception as e:
          print e  
    return keywords

def get_place_keyword():
    place = doc.xpath('//gmd:MD_KeywordTypeCode[@codeListValue="RI_525"]/../../gmd:keyword[@xsi:type="gmd:PT_FreeText_PropertyType"]/gco:CharacterString', namespaces=nspace)
    
    eng=''
    if place and "> CANADA > " in place[0].text:
        eng=place[0].text.split("CANADA > ")[1].title()
        
    elif place:
        eng=place[0].text.title()
   
    try:
        #print geographic_regions[eng]
        return geographic_regions[eng]
    except KeyError,IndexError:
        #print "No Region Found"
        return ''
        
def size(): 
    try:
        s = doc.find('//gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:transferSize/gco:Real', nspace).text   
        return int(round(eval(s)))
    except:
        return ''
package_dict = {'resources': []}  

def resources():

    resources = []
    fileid= package_dict['id']
    path = '//gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine'
    online=doc.xpath(path,namespaces=nspace)
    for node in online:
        
        try:
            resource_dict={}
            resource_dict['url'] = node.find('gmd:CI_OnlineResource/gmd:linkage/gmd:URL', nspace).text
            resource_dict['language']=doc.find('//gmd:MD_DataIdentification/gmd:language/gco:CharacterString', nspace).text
            resource_dict['name']=node.find('gmd:CI_OnlineResource/gmd:description/gco:CharacterString', nspace).text
            resource_dict['name_fra']=node.find('gmd:CI_OnlineResource/gmd:description/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString', nspace).text
            resource_dict['size']=size()
            #protocol = node.find('gmd:CI_OnlineResource/gmd:protocol/gco:CharacterString',nspace).text
            format = doc.find('//gmd:distributionInfo/gmd:MD_Distribution/gmd:distributionFormat/gmd:MD_Format/gmd:name/gco:CharacterString',nspace).text
            
            if format not in formatTypes:
     
                resource_dict['format'] = formatTypes['Other']
            else:
                resource_dict['format'] = formatTypes[format]
           
            resources.append(resource_dict)
        except:
            raise

    #add 2 resource for Geogratis HTML pages
    resource_dict={}
    resource_dict['url'] = "http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/{}.html".format(fileid)
    resource_dict['language']="eng; CAN"
    #resource_dict['size']  Size is not required
    resource_dict['name']="GeoGratis Dataset Record"
    resource_dict['name_fra']=u"Record de jeu de données GeoGratis"
    resource_dict['format']=formatTypes['HTML']
    resources.append(resource_dict)

    resource_dict={}
    resource_dict['url'] = "http://geogratis.gc.ca/api/fr/nrcan-rncan/ess-sst/{}.html".format(fileid)
    resource_dict['language']="fra; CAN"
    resource_dict['name']="GeoGratis Dataset Record"
    resource_dict['name_fra']="Record de jeu de données GeoGratis"
    resource_dict['format']=formatTypes['HTML']
    resources.append(resource_dict)
     
    # Add 2 files for the NAP resources
    resource_dict={}
    resource_dict['url'] = "http://geogratis.gc.ca/api/fr/nrcan-rncan/ess-sst/{}.nap".format(fileid)
    resource_dict['language']="eng; CAN"
    resource_dict['name']=u"ISO 19115 Metadata File"
    resource_dict['name_fra']=u"Fichiers de métadonnées ISO 19115 "
    resource_dict['format']=formatTypes['XML']
    resources.append(resource_dict)
    
    resource_dict={}
    resource_dict['url'] = "http://geogratis.gc.ca/api/fr/nrcan-rncan/ess-sst/{}.nap".format(fileid)
    resource_dict['language']="fra; CAN"
    resource_dict['name']=u"ISO 19115 Metadata File"
    resource_dict['name_fra']=u"Fichiers de métadonnées ISO 19115 "
    resource_dict['format']=formatTypes['XML']
    resources.append(resource_dict) 
    
    package_dict['resources']=resources      

def data_identification():
    #8 of 33
    try:
        fileid=charstring_path('dataSetURI').replace("http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/","")  
    except IndexError:  
        fileid = charstring_path('fileIdentifier')
    package_dict['id'] =fileid #charstring_path('fileIdentifier')
    #package_dict['language']=schema.dataset_field_by_id['language']['example']['eng']
    package_dict['owner_org']='nrcan-rncan'          
    package_dict['topic_category']=get_topic_category()
    package_dict['subject']=get_subject_from_topic_category() 
    package_dict['catalog_type']=u"Geo Data | G\xe9o"
    package_dict['license_id']="ca-ogl-lgo"
    package_dict['presentation_form']=get_presentation_code()
    try:
        package_dict['browse_graphic_url']=full_path('//gmd:MD_BrowseGraphic/gmd:fileName/gco:CharacterString')
    except IndexError:
        package_dict['browse_graphic_url']=''
        
    package_dict['digital_object_identifier']=get_doi()

def time_and_space():
    #10 if 33
    package_dict['date_published']=full_path('//gmd:CI_Date/gmd:date/gco:Date')
    package_dict['date_modified']=''
    package_dict['maintenance_and_update_frequency']=get_update_frequency()
    package_dict['portal_release_date']='2013-05-24'
    package_dict['ready_to_publish']=True
    start,end = get_time()
    package_dict['time_period_coverage_start']=start
    package_dict['time_period_coverage_end']=end
    package_dict['geographic_region']=get_place_keyword()
    package_dict['spatial']=get_spatial()
    package_dict['spatial_representation_type']=get_spatial_rep_type()

def bilingual():
    #14 of 33
    package_dict['data_series_name']=full_path('//gmd:CI_Citation/gmd:series/gmd:CI_Series/gmd:name/gco:CharacterString')
    package_dict['data_series_name_fra']=full_path('//gmd:CI_Citation/gmd:series/gmd:CI_Series/gmd:name/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString')
    package_dict['data_series_issue_identification']=full_path('//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:series/gmd:CI_Series/gmd:issueIdentification/gco:CharacterString')
    package_dict['data_series_issue_identification_fra']=package_dict['data_series_issue_identification']
    package_dict['endpoint_url']='http://geogratis.gc.ca/api/en/'
    package_dict['endpoint_url_fra']='http://geogratis.gc.ca/api/fr/'
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
            
def process(dir,outfile): 
    global doc
    jlfile = open(os.path.normpath(outfile), "w")
    for (path, dirs, files) in os.walk(os.path.normpath(dir)):
        for n,file in enumerate(files):
            #print file
            f = open(os.path.join(path,file),"r")
            doc = etree.parse(f)
            data_identification()
            time_and_space()
            bilingual()
            resources()
            package_dict['validation_override']=True
            #check_structure(package_dict)
            #pprint(json.dumps(package_dict))
            
            if (n % 100) == 0: print n 
            #print package_dict['id']
            jlfile.write(json.dumps(package_dict) + "\n")  


if __name__ == "__main__":
    dir="/Users/peder/dev/OpenData/nrcandump-sample"
    outfile='/Users/peder/dev/goc/LOAD/nrcan-full-%s.jl' % (date.today())

    process(dir,outfile)
    #process()