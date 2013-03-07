'''
Created on 2013-01-10

@author: jakoped

This module is used for converting various items from in the pilot XML
'''
from ckanext.canada.metadata_schema import schema_description
from lxml import etree
from pprint import pprint
import mappings

import sys
import simplejson as json
import string



class Transform:
    
    ''' A 3 pass method for turning pilot xml into CKAN json  
        each file takes a file and produces a new file.
    '''
    def structure(self):
        ''' Step 1:  Create CKAN Structure  '''
        self.out = open("data/pilot-pass1.jl", "w")
        for event, element in etree.iterparse("data/tables_20120815.xml", events=("start","end")):
            
            if event == "start" and  element.tag == "record":
                
                self._process_node(element)
                
            element.clear()
            del element # for extra insurance  
            
        self.out.close()
        pass
    
    def replace(self):
        ''' Step 2:  Replace keys with values from metadata_schema choices  '''
        pass1_in = open("data/pilot-pass1.jl", "r")
        for line in pass1_in:
       
            j = json.loads(line)

            pprint(j)
            sys.exit()
        pass

    def defaults(self):
        ''' Step 3: Fill empty fields with defaults '''
        pass   
    
    def _process_node(self,node):
        
        package_dict = {'extras': {}, 'resources': [], 'tags': []}
        for ckan_name, pilot_name, field in schema_description.dataset_all_fields():
            try: # the simplest case, one to one mapping of values
            # temporary hack because name has not been mapped to thisformid in the schema

                value = node.xpath("FORM[NAME='%s']/A/text()" % pilot_name)[0]
                package_dict[ckan_name] = value
            except IndexError:  #when None, eg. same as elif pilot_name is None:
               package_dict[ckan_name] = ''
            
            # now do resources, use my own logic as 

            resource_fields = {'url':'dataset_link_en_1',
                               'size': 'dataset_size_en_1',
                               'format':'dataset_format_1'}
            resources = []
            resource_dict = {}
            
            resource_dict['name'] = ''
            resource_dict['name_fr'] = ''
            resource_dict['language'] = ''
            resource_dict['last_modified'] = ''
         

            for key,value  in resource_fields.items():
                try:
                    resource_dict[key]  = node.xpath("FORM[NAME='%s']/A/text()" % value)[0]
                    
                except IndexError:
                    resource_dict[key] = ''
                    
            resources.append(resource_dict)
            
            package_dict['resources'] = resources
            
            # now do tags
            
        self.out.write(json.dumps(package_dict) + "\n")
        
def convert_name(thisformid):
    
    name = thisformid.lower().split('-')[0]
    return "%s-%s" % ('statcan',name)
    
def process_record(node):
    package_dict = {'extras': {}, 'resources': [], 'tags': []}
    data = {}
    extras = {}
    resource={}
    resources=[]
    
    for ckan_name, pilot_name, field in schema_description.dataset_all_fields():
        try: # the simplest case, one to one mapping of values
            # temporary hack because name has not been mapped to thisformid in the schema
            
            value = node.xpath("FORM[NAME='%s']/A/text()" % pilot_name)[0]
            pilot_code = value.split('|')
            if pilot_code[0] in mappings.code_mapping_strategies:
                data[ckan_name] = mappings.code_mapping_strategies[pilot_code[0]](pilot_code[1])
            else:

                data[ckan_name] = value
        except UnicodeDecodeError:
            print "UNICODE ERROR"
        except IndexError: #same as elif pilot_name is None:
            if ckan_name == "name": 
                data['name'] = "statcan-" + mappings.random_id()
                print 
            elif ckan_name in mappings.default_strategies:
                data[ckan_name] = mappings.default_strategies[ckan_name]()

            else:
                data[ckan_name] = "default_" + ckan_name
     
        finally: 
            # reorganize dict for CKAN
            if ckan_name in schema_description.extra_package_fields:
               extras[ckan_name] = data[ckan_name]
               del data[ckan_name]  
            # now populate packages
            elif ckan_name == 'url':
                resource['url'] = "http://www.statcan.gc.ca/cgi-bin/sum-som/fl/cstsaveascsv.cgi?filename=arts63a-fra.htm&amp;lan=fre"
                #resource['url'] = node.xpath("FORM['dataset_link_en_1']/A/text()")[0]
            
            elif ckan_name in schema_description.all_resource_fields:
                resource[ckan_name] = "default_package_value " + ckan_name
                
                #if ckan_name != 'name': del data[ckan_name]
#            elif ckan_name in schema_description.all_resource_fields and ckan_name != 'name':  #FIXME
#                print "Resource gets " + ckan_name;
#                resource[ckan_name] = data[ckan_name];
#                del data[ckan_name]               
    
    resources.append(resource)         
    data['extras'] = extras
    data['resources'] = resources
    data['groups'] = ["statcan"]
   
#   extras = {key:value for (key, value) in data if key in schema_description.extra_package_fields}
    s = "some\x00string. with\x15 funny characters"
    foo = filter(lambda x: x in string.printable, s)
    print foo
    valid_utf8 = True
    try:
        foo.decode('utf-8')
    except UnicodeDecodeError:
        valid_utf8 = False
    print valid_utf8
    whatisthis(data)
    data2=json.dumps(data,encoding="utf-8")

    whatisthis(data2)
    data3 = filter(lambda x: x in string.printable, s)
    whatisthis(data3)
    #data = json.dumps(data)
    with open('/Users/peder/Desktop/data.json','w') as outfile:
        json.dump(data,outfile)
 
    sys.exit()
    #ckan_api_client.insert(data)
    #sys.exit()
def whatisthis(s):
    if isinstance(s, str):
        return "ordinary string"
    elif isinstance(s, unicode):
        return "unicode string"
    else:
        return "not a string"

def report(errors):
    print "Record Error: %s" % errors
   
def process_pilot_xml(xml_file):
    # by using the default 'end' event, you start at the _bottom_ of the tree
    for event, element in etree.iterparse(xml_file, events=("start","end")):
        if event == "start" and  element.tag == "record":
            process_record(element)
        element.clear()
        del element # for extra insurance  
             
if __name__ == "__main__":
    #Transform().structure()   
    Transform().replace()
    #process_pilot_xml('data/tables_20120815.xml')

