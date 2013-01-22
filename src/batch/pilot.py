import requests
import os 
import json
from lxml import etree
from ConfigParser import SafeConfigParser
import sys
import pprint
from ckan_api_client import submit

def clean_data():
    class FileResolver(etree.Resolver):
        def resolve(self, url, pubid, context):
            return self.resolve_filename(url, context)

    parser = etree.XMLParser()
    parser.resolvers.add(FileResolver())
    xml_input = etree.parse(open(os.path.normpath('data/pilot.xml')),parser)
    xslt_root = etree.parse(open('data/clean-pilot.xsl'),parser)
    transform = etree.XSLT(xslt_root)
    result = transform(xml_input)
    return result

      

def insert_records(records): 
    
    for record in records.findall('record'):

        package = {}
        for  ckan_name, pilot_name in parser.items('minimal_ckan_field_mappings'):

            try:
                #since we don't have a name, lowercase thisformid 
                '''Temporary Hack'''
                if pilot_name == 'thisformid':
                    package['name'] = record.find('thisformid').text[:8].lower()
                else:   
                    package[ckan_name] = record.find(pilot_name).text
            except AttributeError:                
                pass
            except SyntaxError:
                pass
            except:
                if ckan_name == "groups":
                    package['groups'] = ["statcan"]
                else:     
                    package[ckan_name] = "dummy_"+ ckan_name

        #submit(package)
        pprint.pprint(body, width=200)
        sys.exit()

if __name__ == "__main__":
   
    #read_config()
    #insert_records(clean_data())
    print clean_data()