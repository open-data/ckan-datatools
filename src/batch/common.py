from lxml import etree
from ckanext.canada.metadata_schema import schema_description
from pprint import pprint

nrcan_namespaces = {'gmd': 'http://www.isotc211.org/2005/gmd','gco':'http://www.isotc211.org/2005/gco','gml':'http://www.opengis.net/gml'}
schema_file_formats = [c['key'] for c in schema_description.resource_field_by_id['format']['choices']]
# A dict of list might be easierto use that a list of dicts so  you can pick with langs['eng']
schema_languages = dict((d['eng'],d) for d in schema_description.resource_field_by_id['language']['choices'])


class XmlStreamReader():
    '''  Loads a large XML file as a stream and returns various 
         useful generators.
         Pass the XML file 
         and the root record tag
         '''
    
    def __init__(self,record_tag,xml_file):
        self.xml_file = xml_file
        self.record_tag = record_tag
    
    def _iter_open(self):
        # by using the default 'end' event, you start at the _bottom_ of the tree
        for event, element in etree.iterparse(self.xml_file, events=("start","end")):
            if event == "start" and  element.tag == self.record_tag:
                
                yield element
#                print "Start", element.tag
#            if event == "end" and  element.tag == self.record_tag:
#                #yield element
#                print "End", element 
            #element.clear()
            
    def elements(self):   
        return self._iter_open()

def get_valid_input(input_string, valid_options):
    input_string += " ({}) ".format(", ".join(valid_options))
    response = raw_input(input_string)
    while response.lower() not in valid_options:
        response = input(input_string)
    return response  