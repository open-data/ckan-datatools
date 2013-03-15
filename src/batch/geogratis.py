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
import urllib2
import argparse
from ConfigParser import SafeConfigParser 
from pprint import pprint
from lxml import etree
import geojson
#from itertools import *
from ckanext.canada.metadata_schema import schema_description


        
NEXT = "http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/?alt=json&max-results=50"
LAST_REQUEST =''

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
    pass

def test_single():   
    json_data=open('data/nrcan-single.json')
    data=json.load(json_data)
    create_package(data)
    

def api_call(payload):
    pprint(json.dumps(payload))
    headers = {'Authorization': 'tester'}
    url = u"http://localhost:8080/api/action/package_create"
    headers = {'Authorization': 'tester','content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    print r.status_code
    
def crossReference(fname1,fname2,outfile):
    def findit(id):
        with open(fname2, 'r') as inF:
            for line in inF:
                if id in line:
                    return line

    out = open(outfile, "w")
    x =0
    with open(fname1) as infile:
        for i,line in enumerate(infile):    
            fr = findit(json.loads(line)['id'])
            tup = (i, json.loads(line), json.loads(fr))
            out.write(str(tup) + "\n")
            x+=1
            if x > 2:break
    
        infile.close()
        out.close()
        inF.close()
        '''
        from itertools import izip
        with open(fname1) as f1:
            with open(fname2) as f2:
                for (c1, c2) in izip(f1, car_names(f2)):
                    print c1, c2 
        '''      

class NrcanMunge():
    def __init__(self):        
        pass
 
    def mungeDatasets(self):
        
        with open('/Users/peder/dev/goc/nrcan.links', 'r') as inF:
            for line in inF:
                fr, en = str(line).strip().split(", ")
                print fr, en
                sys.exit()
        self.out.close()   
        
    def camel_to_label(self, ccname):
        """
        Convert a camelcase name with irregularities from our proposed xml file
        to a field label with spaces
    
        >>> camel_to_label(u'relatedDocumentsURL')
        u'Related Documents URL'
        >>> camel_to_label(u'URLdocumentsConnexes')
        u'URL Documents Connexes'
        >>> camel_to_label(u'URIJeuDonnées')
        u'URI Jue Données'
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

    def ola(context, a):
        return "Ola %s" % a
    def loadsofargs(context, *args):
        return "Got %d arguments." % len(args)
  
    def create_ckan_data(self):
        ''' Create ckan ready .jl datasets from .nap XML files  

        '''
        jlfile = open(os.path.normpath('/temp/LOAD/nrcan-try5.jl'), "a")
        presentationCodes = dict((item['id'], item['key']) for item in schema_description.dataset_field_by_id['presentation_form']['choices'])
        maintenanceFrequencyCodes = dict((item['id'], item['key']) for item in schema_description.dataset_field_by_id['maintenance_and_update_frequency']['choices'])
        topicKeys = dict((item['eng'], item['key']) for item in schema_description.dataset_field_by_id['topic_category']['choices'])
        
        nspace = {'gmd': 'http://www.isotc211.org/2005/gmd','gco':'http://www.isotc211.org/2005/gco','gml':'http://www.opengis.net/gml'}
        for (path, dirs, files) in os.walk(os.path.normpath("/temp/nap/en/")):
            for file in files:
                 
                package_dict = {'resources': [], 'tags':[]}
                
                f = open(os.path.join(path,file),"r")
                doc = etree.parse(f)
                   
                try:
                    fr = open(os.path.normpath("/temp/nap/fr/"+ file), "r")
                    doc_fr = etree.parse(fr)
                except IOError:
                    print "File Error"
                    continue

        
                def charstring(key):
                    return doc.xpath(('//gmd:%s/gco:CharacterString' % key),namespaces=nspace)[0].text
                
               
                def georegions():
                    #  replace with list comprehension
                    compass = ['westBoundLongitude','eastBoundLongitude','southBoundLatitude','northBoundLatitude']
                    regions = []
                    for c in compass:
                        
                        regions.append(doc.xpath('//gmd:%s/gco:Decimal' % c,namespaces=nspace)[0].text)
                        
                    return regions
                        
                def clean_tag(x):
                    cleaned =  u''.join(re.findall(u'[\w\-.]+ ?', x, re.UNICODE)).rstrip()  
                    if " > " in cleaned:
                        return 
                    elif "Science Keywords" in cleaned:
                        return
                    elif "CONTINENT" in cleaned:
                        return
                    else:
                        return cleaned
                    
                
                def charstring_fr(key):
                    return doc_fr.xpath(('//gmd:%s/gco:CharacterString' % key),namespaces=nspace)[0].text
                    pass
                
                package_dict['language'] =''
                package_dict['author'] = "Natural Resources Canada | Ressources naturelles Canada"
                package_dict['department_number'] =''
                package_dict['author_email'] =''
                package_dict['title'] = charstring('title')
                package_dict['title_fra'] = charstring_fr('title')
                package_dict['name'] = file.split(".")[0]
                package_dict['notes']=charstring('abstract')
                package_dict['notes_fra']=charstring_fr('abstract')
                package_dict['catalog_type']="Geo Data | G\u00e9o"
                package_dict['digital_object_identifier']= ''
                topic_name_en = self.camel_to_label(doc.xpath('//gmd:MD_TopicCategoryCode',namespaces=nspace)[0].text)
                try:
                    package_dict['topic_category'] = topicKeys[topic_name_en]
                except KeyError:
                    package_dict['topic_category'] =''
                    
                package_dict['subject']=''
                
                #item['id'], item['key']) for item in schema_description.dataset_field_by_id['presentation_form']['choices']
                keywords = doc.xpath('//gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword/gco:CharacterString',namespaces=nspace)
                keywords_fr = doc_fr.xpath('//gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword/gco:CharacterString',namespaces=nspace)
                #print keywords
                tags = []
                en_tags = [t.text for t in keywords]
                fr_tags = [t.text for t in keywords_fr]
                tags = [{'name': clean_tag(en) + u'  ' + clean_tag(fr)} for en, fr in zip(en_tags, fr_tags) if clean_tag(en)]

                package_dict['tags'] = tags
                package_dict['license_id']=''
                package_dict['data_series_name']=''
                try:
                    package_dict['data_series_name']=doc.xpath('//gmd:CI_Citation/gmd:series/gmd:CI_Series/gmd:name/gco:CharacterString',namespaces=nspace)[0].text
                    package_dict['data_series_name_fra']=doc_fr.xpath('//gmd:CI_Citation/gmd:series/gmd:CI_Series/gmd:name/gco:CharacterString',namespaces=nspace)[0].text
                except IndexError:
                    pass
                package_dict['data_series_issue_identification']=doc.xpath('//gmd:issueIdentification/gco:CharacterString',namespaces=nspace)[0].text
                package_dict['data_series_issue_identification_fra']=doc_fr.xpath('//gmd:issueIdentification/gco:CharacterString',namespaces=nspace)[0].text
                #documentation_url_fra=
                try:
                    frequencyCode = doc.xpath('//gmd:MD_MaintenanceFrequencyCode',namespaces=nspace)[0].attrib['codeListValue'].split("_")[1]
                    package_dict['maintenance_and_update_frequency']=maintenanceFrequencyCodes[int(frequencyCode)]
                except IndexError:
                    package_dict['maintenance_and_update_frequency']=''
                    pass

                time = doc.xpath('//gml:begin/gml:TimeInstant/gml:timePosition',namespaces=nspace)
                #end = doc.xpath('/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:begin/gml:TimeInstant/gml:timePosition',namespaces=nspace)
               
                try:
                    package_dict['temporal_element']= '%s/%s' % (time[0].text,time[1].text)
         
                except IndexError:
                    package_dict['temporal_element']=''
   
                package_dict['geographic_region']=" ".join(georegions())
                package_dict['url']=('http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/%s.html' % package_dict['name'])
                package_dict['url_fra']=('http://geogratis.gc.ca/api/fr/nrcan-rncan/ess-sst/%s.html' % package_dict['name'])
                package_dict['endpoint_url']='http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/'
                package_dict['endpoint_url_fr']='http://geogratis.gc.ca/api/fr/nrcan-rncan/ess-sst/'
                package_dict['date_published']=doc.xpath('//gmd:CI_Date/gmd:date/gco:Date',namespaces=nspace)[0].text
                #ackage_dict['spatial_representation_type']=  spatial represnentation type number
                package_dict['spatial']=''#geojson.dumps(geojson.Point(georegions()))

                try:
                    pCode = doc.xpath('//gmd:CI_PresentationFormCode',namespaces=nspace)[0].attrib['codeListValue'].split("_")[1]
                    package_dict['spatial_representation_type'] = presentationCodes[int(pCode)]
                except IndexError:
                    package_dict['spatial_representation_type'] =''
                
                package_dict['presentation_form']= presentationCodes[int(pCode)]
                #package_dict['browse_graphic_url']='http://wms.ess-ws.nrcan.gc.ca/wms/mapserv?map=/export/wms/mapfiles/reference/overview.map&mode=reference&mapext=%s' % package_dict['geographic_region']
                package_dict['browse_graphic_url']=''

                '''
                package_dict['data_series_name_fra']=
                package_dict['data_series_issue_identification_fra']=
                package_dict['documentation_url_fra']=
                package_dict['related_document_url_fra']=
                package_dict['url_fra']=
                package_dict['endpoint_url_fra']=
                '''
                
                ''' Resources ''' 
                fileurl=doc.xpath('/gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource/gmd:linkage/gmd:URL',namespaces=nspace)
                resources = []
                for f in fileurl:
                    #print f.tag, f.text
                    resource={'url':f.text}
                    resources.append(resource)
                package_dict['resources'] = resources
                ''' Franco Resources '''
            
                #print package_dict['name']
                #f1 = open(os.path.normpath("/temp/nrcan-try1s.jl"), "w")
                
                
                #f1.write(json.dumps(package_dict) + "\n") 
 
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
            
    def save_nap_files(self):
        opener = urllib2.build_opener()
        infile = open(os.path.normpath('/temp/nrcan.links'), "r")
        ''' Grab NRCan .nap xml files and dump into as files into a folder '''
        do = True
        for line in infile:
            en, fr = str(line).strip().split(', ')
            if do:
                logfile = open(os.path.normpath('/temp/nrcan-nap.log'), "a")
                req = urllib2.Request(en)  
                try: 
                    f = opener.open(req,timeout=500)
                    data_en = f.read()
                    print en
                    
                    filename = en.split('/')[-1]
                    print filename 
                    napfile = open(os.path.normpath('/temp/nap/%s' % filename), "w")
                    napfile.write(data_en)
                    napfile.close()
                    logfile.write(filename + ", OK\n")
                except socket.timeout:
                    logfile.write(filename + ", Socket timeout\n")
                
                except: 
                    logfile.write(filename + ", " + str(sys.exc_info()[0]) + "\n")
               
               
                logfile.close()
                sys.exit()
           
    def read_nrcan_data(self):
           ''' Read links from enercan and save them into bilinguages dataset file or database '''
           config = SafeConfigParser()
           config.read('nrcan.config')
           opener = urllib2.build_opener()
           infile = open(os.normpath('/temp/nrcan.links', "r"))
           outfile = open(os.normpath('/temp/nrcan.dat', "w"))
           for line in infile:
               links = str(line).strip("\n").split(', ')
               req = urllib2.Request(links[0])  
               try: 
                   f = opener.open(req,timeout=50)
               except socket.timeout:
                   print "socket timeout"
               package_dict = {'extras': {}, 'resources': [], 'tags': []}
               response = f.read() 
               n = json.loads(response)
               # create english fields
    
               for ckan, nrcan in config.items('package'):
                   if nrcan == "SELECT":
                      print "SELECT"
                      package_dict[ckan] = schema_description.dataset_field_by_id[ckan]['choices'][1]['key']
                   elif "$." in nrcan:
                       print "Use JSON Path"
                       print nrcan
                       print jsonpath(n, nrcan)
                   elif nrcan:
                       print n[nrcan]
                       package_dict[ckan] = n[nrcan]
    
               pprint(package_dict)
    
               sys.exit()
               pass
    
if __name__ == "__main__":
    #report("/Users/peder/dev/goc/nrcan.jl","/Users/peder/dev/goc/nrcan2-fr.jl","/Users/peder/dev/goc/nrcan-combined.txt")
    #test_single()
    NrcanMunge().create_ckan_data()
    '''
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action='store_true')
    parser.add_argument('action', help='The Action you wish to perform on the data', action='store',choices=['init','list','update','report'])
    parser.add_argument('entity', help='The data entity you wish to operate on', action='store',choices=['org','group','user','pack'])
      
    args = parser.parse_args()
    print args
    '''
 

        

