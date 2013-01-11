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
    xml_input = etree.parse(open(os.path.normpath('../harvesters/testdata/pilot.xml')),parser)
    xslt_root = etree.parse(open('clean-pilot.xsl'),parser)
    transform = etree.XSLT(xslt_root)
    result = transform(xml_input)
    return result

def external_list_approach():
    lines = [line.strip() for line in open('fields.txt')]
    return lines
      
def read_config():
    global parser
    parser = SafeConfigParser()
    parser.read('pilot-batch.config')

def insert_records(records): 
    
    for record in records.findall('record'):

        package = {}
        for  ckan_name, pilot_name in parser.items('minimal_ckan_field_mappings'):

            try:
                #since we don't have a name, we need just use the thisformid, but it needs to be lower case
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
                    package['groups'] = ["david"]
                else:     
                    package[ckan_name] = "dummy_"+ ckan_name

        submit(package)
        #pprint.pprint(body, width=200)

if __name__ == "__main__":
   
    #read_config()
    #insert_records(clean_data())
    print clean_data()