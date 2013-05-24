#-*- coding:UTF-8 -*-
''' 
    This module is used to read data from the Geogratis web services into two master data files, 
    one in english and one in french.
    Then tools are provided to generate reports on the data and import it into CKAN  etc. 
'''

import os
import re
import sys
import json
import time
import socket 
import warnings
import urllib2
from datetime import date,datetime
from string import Template
import argparse
import logging
from ConfigParser import SafeConfigParser 
from pprint import pprint
from lxml import etree
import geojson
from excepts  import NestedKeyword, CodedKeyword, EmptyKeyword
from collections import Counter
import common
from common import get_valid_input

from common import XPather
from ckanext.canada.metadata_schema import schema_description

       
NEXT = "http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/?alt=json&max-results=50"
LAST_REQUEST =''
 
validation_override=False               

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

def gather_products():
    global total_download
    global LAST_REQUEST
    global NEXT
    #if LAST!='':NEXT="http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/?alt=json&max-results=50&start-index=%s" % LAST_REQUEST
    total_download = 0
    data = []
    opener = urllib2.build_opener()
    while True:
 
        try:
            req = urllib2.Request(NEXT+'&alt=json')
            f = opener.open(req,timeout=500)
            #print req.has_header('Content-Length')

        except urllib2.URLError:
            #start again where we left off
            # or I could just wait for 5 min, then try 
            # f = opener.open(req,timeout=300) again
            #gather_stage(LAST_REQUEST)
            req = urllib2.Request(NEXT+'&alt=json')
            f = opener.open(req,timeout=50)
        except socket.timeout:
            print "socket timeout"
            
        response = f.read()
        json_response = json.loads(str(response),"utf-8")
        
        # Get the link to the next batch of links
        links = json_response['links']
        for  link in links:
            if link['rel']=='next': 
                NEXT = link['href'] 
                LAST_REQUEST=NEXT
                break

        for product in json_response['products']:     
            file.write(product);  
            file.write(",")
 


class NrcanMunge():
    logging.basicConfig(filename="/Users/peder/dev/goc/ckan-logs/nrcan-munge.log", level=logging.ERROR)
    def __init__(self):        
        pass
        
 
    def mungeDatasets(self):
        
        with open('/Users/peder/dev/goc/nrcan.links', 'r') as inF:
            for line in inF:
                fr, en = str(line).strip().split(", ")
        self.out.close()   
    
    
    def camel_to_label(self, ccname):
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

  
    def create_ckan_data(self,basepath,jlfile,start=0,stop=172000):
        ''' Create ckan ready .jl datasets from .nap XML files  

        '''
        jlfile = open(os.path.normpath(jlfile), "w")
        xpather = XPather(common.nrcan_namespaces)


        # For some reason, Pydev does not like this type of dict comprehension
        #{ choice['id']:choice['key'] for choice in schema_description.dataset_field_by_id['presentation_form']['choices']}
        presentationCodes = dict((choice['id'],choice['key']) for choice in schema_description.dataset_field_by_id['presentation_form']['choices'])
        spatialRepTypeCodes = dict((choice['id'],choice['key']) for choice in schema_description.dataset_field_by_id['spatial_representation_type']['choices'])
        maintenanceFrequencyCodes = dict((item['id'], item['key']) for item in schema_description.dataset_field_by_id['maintenance_and_update_frequency']['choices'])
        topicKeys = dict((item['eng'], item['key']) for item in schema_description.dataset_field_by_id['topic_category']['choices'])
        formatTypes=dict((item['eng'], item['key']) for item in schema_description.resource_field_by_id['format']['choices'])
     
        nspace = common.nrcan_namespaces
        n = 0
        for (path, dirs, files) in os.walk(os.path.normpath(basepath+"/en/")):
            # only process the range required

            for file in files:
                n+=1
                if n<start or n>stop: continue
                package_dict = {'resources': [], 'tags':[]}
                if ".nap" not in file: continue
                f = open(os.path.join(path,file),"r")
                doc = etree.parse(f)
                xpather.set_tree(doc)
                   
                try:
                    fr = open(os.path.normpath(basepath+"/fr/"+ file), "r")
                    doc_fr = etree.parse(fr)
                    xpather.set_tree_fr(doc_fr)
                except IOError as e:
                    logging.error("{}::{}".format(file,e))
                    continue
        
                def charstring(key):
                    return doc.xpath(('//gmd:%s/gco:CharacterString' % key),namespaces=nspace)[0].text
                
               
                def georegions():
                    #  replace with list comprehension
                    # this should be similar to minx, miny, maxx, maxy
                    boundingBox = ['westBoundLongitude','southBoundLatitude','eastBoundLongitude','northBoundLatitude']
                    regions = []
                    for line in boundingBox:
                        
                        regions.append(doc.xpath('//gmd:%s/gco:Decimal' % line,namespaces=nspace)[0].text)
                        
                    return regions
                        
                def clean_tag(x):
                    #replace forward slashes and semicolon so keywords will pass validation
                    #Apostrophes in french words causes a proble; temporary fixx
                    x = x.replace("/"," - ").replace("; ","-")

                    return x.split(">")[-1].lower().strip().capitalize()
                
                def charstring_fr(key):
                    return doc_fr.xpath(('//gmd:%s/gco:CharacterString' % key),namespaces=nspace)[0].text
                    pass
                package_dict['organization'] = 'nrcan-rncan'
                #package_dict['group'] = 'nrcan-rncan'# See if this solves the problem with org not showing up in CKAN
                package_dict['owner_org'] = '9391E0A2-9717-4755-B548-4499C21F917B'  #FIXME
                package_dict['author'] = "Natural Resources Canada | Ressources naturelles Canada"
                package_dict['department_number'] ='115'
                package_dict['author_email'] =xpather.query('author_email','//gmd:electronicMailAddress/gco:CharacterString')
                
                package_dict['title'] = xpather.query('title',
                            '//gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString')
                package_dict['title_fra'] = xpather.query('title_fra',
                            '//gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString')
                
                package_dict['id'] = file.split(".")[0]
                #notes=charstring('abstract')
                notes=xpather.query('notes','//gmd:abstract/gco:CharacterString')
                notes_fra=xpather.query('notes_fra','//gmd:abstract/gco:CharacterString')
                
                
                if 'Abstract not available' in notes:
                    package_dict['notes']="Abstract not available."
                    package_dict['notes_fra']=u"Résumé non disponible."
                    
                else:
                    package_dict['notes']=notes
                    package_dict['notes_fra']=notes_fra

          
                package_dict['catalog_type']=u"Geo Data | G\xe9o"
                package_dict['digital_object_identifier']= ''
                package_dict['ready_to_publish']='0'
                topic_name_en = self.camel_to_label(doc.xpath('//gmd:MD_TopicCategoryCode',namespaces=nspace)[0].text)
                try:
                    package_dict['topic_category'] = topicKeys[topic_name_en]
                except KeyError as e:
                    logging.error("{}::{}".format(file,e))
                    package_dict['topic_category'] =''
                    
                package_dict['subject']=''
                

                keywords = doc.xpath('//gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword/gco:CharacterString',namespaces=nspace)
                keywords_fr = doc_fr.xpath('//gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword/gco:CharacterString',namespaces=nspace)
           
                en_tags = [clean_tag(t.text) for t in keywords]  # must remove forward slashes to pass validation
                
                # Get rid of commans in keywords if they exist
                #en_tags = [tag.strip() for orig in en_tags for tag in orig.split(",")]
                fr_tags = [clean_tag(t.text) for t in keywords_fr]
                #fr_tags = [tag.strip() for orig in fr_tags for tag in orig.split(",")]
                #tags = [{'name': clean_tag(en) + u'  ' + clean_tag(fr)} for en, fr in zip(en_tags, fr_tags) if clean_tag(en) and (len(clean_tag(en)) + len(clean_tag(fr))) < 96]
    
                #package_dict['tags'] = tags
                # Tags are now gone, replaced by en, fr lists of comma delimited keywords
               
                package_dict['keywords'] = ",".join(en_tags)
                package_dict['keywords_fra'] = ",".join(fr_tags)
               
                package_dict['license_id']=''
                
                package_dict['data_series_name']=xpather.query('data_series_name',
                                            '//gmd:CI_Citation/gmd:series/gmd:CI_Series/gmd:name/gco:CharacterString')
                package_dict['data_series_name_fra']=xpather.query('data_series_name_fra',
                                            '//gmd:CI_Citation/gmd:series/gmd:CI_Series/gmd:name/gco:CharacterString')

                package_dict['data_series_issue_identification']=doc.xpath('//gmd:issueIdentification/gco:CharacterString',namespaces=nspace)[0].text
                package_dict['data_series_issue_identification_fra']=doc_fr.xpath('//gmd:issueIdentification/gco:CharacterString',namespaces=nspace)[0].text

                try:
                    frequencyCode = doc.xpath('//gmd:MD_MaintenanceFrequencyCode',namespaces=nspace)[0].attrib['codeListValue'].split("_")[1]
                    print frequencyCode
                    package_dict['maintenance_and_update_frequency']="As Needed | Au besoin"

                    
                except IndexError, TypeError:
                    package_dict['maintenance_and_update_frequency']="As Needed | Au besoin"
                    #print "Eror", package_dict['maintenance_and_update_frequency']
                #ISO 8061
                time = doc.xpath('//gml:begin/gml:TimeInstant/gml:timePosition',namespaces=nspace)
                #end = doc.xpath('/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:begin/gml:TimeInstant/gml:timePosition',namespaces=nspace)

                try:         
                    t = common.time_coverage_fix(time[0].text,time[1].text)
                    package_dict['time_period_coverage_start'] = common.timefix(t[0])
                    package_dict['time_period_coverage_end'] =  common.timefix(t[1])

         
                except IndexError, ValueError:
                   
                    package_dict['time_period_coverage_start'] = ''
                    package_dict['time_period_coverage_end'] = ''
                    

                package_dict['geographic_region']=""#.join(georegions())
                #package_dict['url']=''#('http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/%s.html' % package_dict['name'])
                #package_dict['url_fra']=''#('http://geogratis.gc.ca/api/fr/nrcan-rncan/ess-sst/%s.html' % package_dict['name'])
                package_dict['endpoint_url']='http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/'
                package_dict['endpoint_url_fra']='http://geogratis.gc.ca/api/fr/nrcan-rncan/ess-sst/'
                package_dict['date_published']=doc.xpath('//gmd:CI_Date/gmd:date/gco:Date',namespaces=nspace)[0].text
                
                
                #cornerPoints = doc.xpath('//gmd:cornerPoints/gml:Point/gml:pos',namespaces=nspace)
                #points = [p.text for p in  cornerPoints]  TODO: Figure out overlap between two representations, rings and points
                exteriorRing = doc.xpath('//gml:Polygon/gml:exterior/gml:LinearRing/gml:pos',namespaces=nspace)   
                interiorRing = doc.xpath('//gml:Polygon/gml:interior/gml:LinearRing/gml:pos',namespaces=nspace)   
                extent_template = Template('''{"type": "Polygon", "coordinates": [[[$minx, $miny], [$minx, $maxy], [$maxx, $maxy], [$maxx, $miny], [$minx, $miny]]]}''')

                extRingPoints = [map(float,p.text.split()) for p in  exteriorRing]
                
               
                intRingPoints = [p.text.split(" ") for p in interiorRing]
                if extRingPoints:
                    package_dict['spatial']=geojson.dumps(geojson.geometry.Polygon([extRingPoints]))    
                                          
                else: 
                    package_dict['spatial']=extent_template.substitute(
                                                                        minx = georegions()[0],
                                                                        miny = georegions()[1],
                                                                        maxx = georegions()[2],
                                                                        maxy = georegions()[3]
                                                                        )
                    
                
                
                try:
                    pCode = doc.xpath('//gmd:MD_SpatialRepresentationTypeCode',namespaces=nspace)[0].attrib['codeListValue'].split("_")[1]
                    package_dict['spatial_representation_type'] = spatialRepTypeCodes[int(pCode)]
                except IndexError:
                    package_dict['spatial_representation_type'] =''
                except KeyError:
                    print "Spatial Rep Type not in Schema", int(pCode)
              
                except:
                    raise
                    
           
                try:
                    pCode = doc.xpath('//gmd:CI_PresentationFormCode',namespaces=nspace)[0].attrib['codeListValue'].split("_")[1]
                except IndexError:
                    print "No presentation Form"
                    package_dict['presentation_form'] =''
                except KeyError:
                    print "Presentation code not in Schema"
                    print int(pCode), spatialRepTypeCodes
                
                try:
                    package_dict['presentation_form']= presentationCodes[int(pCode)]
                except KeyError:
                    ''' Default to  u'id': 387,
                       u'key': u'Document Digital | Document num\xe9rique'}
                    '''
                    print "Presentation Code Missing", pCode
                    package_dict['presentation_form']= presentationCodes[387]
                  
        
                #package_dict['browse_graphic_url']='http://wms.ess-ws.nrcan.gc.ca/wms/mapserv?map=/export/wms/mapfiles/reference/overview.map&mode=reference&mapext=%s' % package_dict['geographic_region']
                package_dict['browse_graphic_url']=xpather.query('browse_graphic_url','//MD_BrowseGraphic/gmd:fileName/gco:CharacterString')
                if package_dict['browse_graphic_url'] == '':
                    pass
                    #package_dict['browse_graphic_url'] ='http://www.fakeimageurl123.com/foo.jpg'
                    
                
                #TODO:  gmd:otherCitationDetails for DOI
                ''' Resources ''' 
                resources = []
                resour=doc.xpath('//gmd:CI_OnlineResource',namespaces=nspace)
                # search only this resource tree to avoid repetition
                # keep track of duplicates
                resource_track =[]
                for r in resour:
                    try:
                        url = r.find('gmd:linkage/gmd:URL', nspace).text
                        #check for duplicates
                        #if url in resource_track: continue
                        # we don't want ftp links and other unknown or incomplete urls
                        #if "http://" not in url: continue
                        try:
                            format = r.find('gmd:name/gco:CharacterString', nspace).text
                        except AttributeError:
                            #r.find('gmd:name/gco:CharacterString', nspace). returns NoneType
                            format =  formatTypes['Other']
                     
                        if format in formatTypes:
                            
                            format = formatTypes[format]
                        else:
                           
                            format =  formatTypes['Other']
                        
                        resource_track.append(url)
                        
                        lang = doc.find('//gmd:MD_DataIdentification/gmd:language/gco:CharacterString', nspace).text
                       
                        #TODO :  Need more information on whether we should actually exclude files via the schema
                        resource={'url':url,'format':format,'language':lang,'resource_type': 'file', 'name':'Dataset'}
                        '''
                        for schema_format in  common.schema_file_formats:
                            if  format == schema_format:
                                resource={'url':url,'format':format,'language':lang, 'name':'Dataset'}
                        '''
                        resources.append(resource) 
                        #print resource 
                       
                    except Exception as e:
                        raise
                        #print "Resource Exception ",  e
                        continue
                        
                #pprint(resources)
                package_dict['validation_override']=validation_override
                package_dict['resources'] = resources    
                package_dict['portal_release_date']='2013-05-24'
                package_dict['ready_to_publish']=True          
                #pprint (package_dict)
                
                if (n % 100) == 0: print n 

                jlfile.write(json.dumps(package_dict) + "\n")  
             
         
    def write_new_links(self): 
        infile = open(os.path.normpath('/temp/nrcan2.links'), "r")   
        links = open(os.path.normpath('/temp/nrcan3.links'), "w")
        start = False
        for line in infile:
            en, fr = str(line).strip().split(', ')
            if start:
                print "WRITE", en
                links.write(line)
            elif en == "http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/56bb6177-1364-4fe3-8515-16d94dcef79f.nap":
                start = True
            else:
                print "SKIP", en

               
def download_nap(linkfile,outpath):
    
        """
        A simple funtion to fetch .nap files from Geogratis.
    
            :param linkfile: A file with a list of links to nap files. Example: 
                             http://geogratis.gc.ca/api/fr/nrcan-rncan/ess-sst/16d4b644-6ba0-4893-b85e-c5c883f1b875.nap
            :param outpath:  The local path in which to store .nap files
            
        """
        
        infile = open(os.path.normpath(linkfile), "r")

        for line in infile:
                print line
                req = urllib2.Request(line)  
                try: 
                    f = urllib2.urlopen(req,timeout=500)
                    data = f.read()
   
                    napfile = open(os.path.normpath('%s/%s' % (outpath,filename), "w"))
                    napfile.write(data)
                    napfile.close()
                except urllib2.HTTPError as h:
                    print h   
                except socket.timeout as s:
                    print s          

           
if __name__ == "__main__":
    validation_override=True
#    NrcanMunge().create_ckan_data(basepath="/Users/peder/dev/goc/nap-sample",
#                                     jlfile='/Users/peder/dev/goc/LOAD/nrcan-test.jl',start=0,stop=250)


    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('action', help='Build a dataset', action='store',choices=['full', 'short', 'test','download'])
    #parser.add_argument("-p", "--path", help="file or dir", action='store_true')

    args = parser.parse_args()
    def bypass_cli(command):
        class Object(object):
            pass
        args= Object()
        args.action =command
    
    if args.action == 'full':
       print "You are about to write a new .jl file from the geogratis dataholdings. This could take a long time."
       NrcanMunge().create_ckan_data(basepath="/Users/peder/dev/goc/nap",
                                     jlfile='/Users/peder/dev/goc/LOAD/nrcan-full-%s.jl' % (date.today()))

    elif args.action == 'test':
       NrcanMunge().create_ckan_data(basepath="/Users/peder/dev/goc/nap-sample",
                                     jlfile='/Users/peder/dev/goc/LOAD/nrcan-test.jl',start=0,stop=25)

    elif args.action == 'short':
       NrcanMunge().create_ckan_data(basepath="/Users/peder/dev/goc/nap",
                                     jlfile='/Users/peder/dev/goc/LOAD/nrcan-short-%s.jl'% (date.today()),start=0,stop=1000)

    elif args.action == 'download':
        download_nap('/Users/peder/dev/goc/ckan-logs/download_missing_fr.links',
                     '/Users/peder/dev/goc/nap/missing/fr')
