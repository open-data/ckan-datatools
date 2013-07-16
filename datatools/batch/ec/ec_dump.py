#-*- coding:UTF-8 -*-
import os
import sys
from lxml import etree
from pprint import pprint
import json
from datetime import date
from datatools import helpers
from datatools.batch import common
from datatools.batch.nrcan import nrcan_dump as nrcan_dump
from ckanext.canada.metadata_schema import schema_description as schema

formatTypes=dict((item['eng'], item['key']) for item in schema.resource_field_by_id['format']['choices'])
nspace = common.nap_namespaces


def size(doc): 
    try:
        s = doc.find('//gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:transferSize/gco:Real', nspace).text   
        # Convert MB fractions to bytes rounded  2**20 MegaBiByte binary megabyte
        return int(round((eval(s) * (2**20))))
    except:
        return ''

def language(doc):
    lang = doc.find('//gmd:MD_DataIdentification/gmd:language/gco:CharacterString', nspace).text
    if lang=='eng': lang='eng; CAN'
    if lang=='fra': lang='fra: CAN'
    return lang

def resources(doc):
    
    resources = []
    path = '//gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine'
    online=doc.xpath(path,namespaces=nspace)
    for node in online:
        print "got node"
        try:
            resource_dict={}
            resource_dict['url'] = node.find('gmd:CI_OnlineResource/gmd:linkage/gmd:URL', nspace).text

            resource_dict['name']=node.find('gmd:CI_OnlineResource/gmd:description/gco:CharacterString', nspace).text
            resource_dict['language']= node.attrib['{http://www.w3.org/1999/xlink}role'].split(':')[-1]
            #=node.find('[@xlink:role]')
                
            resource_dict['name_fra']=node.find('gmd:CI_OnlineResource/gmd:description/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString', nspace).text
            resource_dict['resource_type']='file'
            resource_dict['size']=size(doc)
            
#            print "Format ", format
#            global_format = node.find('gmd:MD_Distribution/gmd:distributionFormat/gmd:MD_Format/gmd:name/gco:CharacterString',nspace)
#            
#            print "Global Format",global_format
            try:
                format = node.find('gmd:CI_OnlineResource/gmd:name/gco:CharacterString',nspace).text
                if format == format not in formatTypes:
                    resource_dict['format'] = formatTypes['Other']
                else:
                    resource_dict['format'] = formatTypes[format]
            except AttributeError: 
                resource_dict['format'] = formatTypes['Other']
            resources.append(resource_dict)
        except AttributeError:
            # probably just means there are no values for names
            raise
            pass
        except:
            raise

    print resources
    return resources      

def process(dir,outfile): 
    counter=0
    jlfile = open(os.path.normpath(outfile), "w")
    for (path, dirs, files) in os.walk(os.path.normpath(dir)):
        for file in files:
            if file =='metadata.iso19139.xml':
                counter+=1
                f = open(os.path.join(path,file),"r")
                doc = etree.parse(f)
                print f, doc
                nrcan_dump.doc = doc
                nrcan_dump.data_identification()
                
                nrcan_dump.time_and_space()
                
                nrcan_dump.bilingual()
                nrcan_dump.package_dict['resources'] = resources(doc)
               
                print counter, nrcan_dump.package_dict['id']
                #nrcan_dump.check_structure(nrcan_dump.package_dict)
                nrcan_dump.package_dict['owner_org']='ec'
#                nrcan_dump.package_dict['browse_graphic_url']= "NPRI_s.png"             
#                nrcan_dump.package_dict['endpoint_url_fra']= "http:"
#                nrcan_dump.package_dict['endpoint_url']= ""
                nrcan_dump.package_dict['url']= "http://www.ec.gc.ca/default.asp?lang=En"
                nrcan_dump.package_dict['url_fra']= "http://www.ec.gc.ca/default.asp?lang=Fr"
                
                pprint(nrcan_dump.package_dict)
                
                #jlfile.write(json.dumps(nrcan_dump.package_dict) + "\n")  

if __name__ == "__main__":
    
    outfile =helpers.load_dir()+"ec.jl"
    dir="/Users/peder/dev/OpenData/data_sources/ec/"

    process(dir,outfile)