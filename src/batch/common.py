from lxml import etree
import os
from ckanext.canada.metadata_schema import schema_description
from pprint import pprint
import logging

''' Namespaces required to query .nap files with XPath '''
nrcan_namespaces = {'gmd': 'http://www.isotc211.org/2005/gmd','gco':'http://www.isotc211.org/2005/gco','gml':'http://www.opengis.net/gml'}


schema_file_formats = [c['key'] for c in schema_description.resource_field_by_id['format']['choices']]
# A dict of list might be easierto use that a list of dicts so  you can pick with langs['eng']
schema_languages = dict((d['eng'],d) for d in schema_description.resource_field_by_id['language']['choices'])


''' Checking to see if a File format is in the schema happens both in geogratis and in reports  '''

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

logging.basicConfig(filename="/Users/peder/dev/goc/ckan-logs/xpath.log", level=logging.ERROR)

def xml_generator(filedir):
        """
            walk through nap files folder to parse and return xml
            
            param filedir:  The directory containing the nap files
        """
        for (path, dirs, files) in os.walk(os.path.normpath(filedir)):
            for n, file in enumerate(files):
                # All non nap files should be ignored
                if ".nap" not in file:continue
                f = open(os.path.join(path,file),"r")
                yield etree.parse(f)

class XPather:
    """Using a class in this instance means not having to pass the same parms to query, so it promotes reusability
    
    """
    
    def __init__(self,namespaces):
        self.nspace = namespaces
        
    
    def set_tree(self,doc):
        """Set the default Etree document 
        
        Keyword Arguments:
        doc -- the default Etree Object that the query is performed on
        """
        
        self.doc = doc
    def set_tree_fr(self,doc_fr):
        """Set the default Etree document 
        
        Keyword Arguments:
        doc -- the default Etree Object that the query is performed on
        """
        
        self.doc_fr = doc_fr
    
    def query(self,key,query_path): 
        
            
            """Return value from an XPath query on a document, or return empty string and log excption.
            This method is used extensively in both .jl file creating and reporting
            doc -- an Etree Object that the query is performed on .  This is use to override the default if there is
                   a french version of the xml that has to be processes
                   
            Keyword Arguments:
            key -- the key in the dictionary that the caller is trying to set.  Used for logging
            
            qpath -- the xpath query string
                  
            This method does not deal with the logic of how to react to failures, it merely logs it. 
            Any validation logic or possible default values as a result of empty values are left to the caller.
            
            
            """

            try: 
                if "_fra" in key:
                    return self.doc_fr.xpath(query_path,namespaces=self.nspace)[0].text 
                else: 
                    return self.doc.xpath(query_path,namespaces=self.nspace)[0].text 
            except Exception as e: 
                logging.error("{}::{}".format(key,e))
                return ""
            
