# coding=utf-8
from lxml import etree
import os
import csv
import cStringIO
import codecs
from datetime import date, datetime
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
        
            
            """
            Return value from an XPath query on a document, or return empty string and log excption.
            This method is used extensively in both .jl file creating and reporting
            
            param doc: an Etree Object that the query is performed on .  This is use to override the default if there is
                   a french version of the xml that has to be processes

            param key: the key in the dictionary that the caller is trying to set.  Used for logging
            
            param qpath: the xpath query string
                  
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

''' This could be lowercased to reduce number of hits, but then reporting 
would be less useful.  THE ORDER OF THIS LIST IS VERY IMPORTANT in order check to return at the right spot.  
Put cases that can be misunderstood last '''
language_markers=[
                   (' - (In English)', ' - (In French)'),
                    (' (In English)', ' (In French)'),
                   (' - English Version [AAFC', ' - French Version [AAFC'),
                   (' - English Version',' - French Version'),
                   (' - English version',' - French version'),
                    (' (in English)', ' (in French)'),
                    (' - (in English)', ' - (in French)'),
                    (' (English version)', ' (French version)'),
                    (' (English verison)', ' (French version)'),
                    (' - (in English)', ' - (in French)'),
                    (' (in english)', ' (in french)'),
                    (' - (in english)', ' - (in french)'),
                    (' - (English)', ' - (French)'),  
                    (' - ENGLISH VERSION', ' - FRENCH VERSION'),
                    (' - English', ' - French'),]

language_markers_fra = [
                         u' (Version anglaise)',
                         u' (Version française)',
                         u' - version française [AAFC',
                         u' - version anglaise [AAFC',
                         u' - version anglaise',
                         u' - version française',
                         u' (en anglais)', 
                         u'- version anglaise',
                         u' (version anglaise)',
                       ]

foobared_title_filters=['(French verison)', '(Fench version)']

'''
Some fiscal tables are marked bilingual, but infact they are not. Find language in URL.
Filter out bilingual
Finance Dat  

Historial Project data set 2005-2006  -   No resources   several records have in withous resources other than HTML.
Parsing problems with Keywords, sometimes keyword is just a blank box: Historical PRoject Dataset 2005-2006
Dateset with no keywords should go wihtout keywords.  They should still go in. 
2008  Public Service Employee Survey (PSES) results   one xsl file marked as 2 different HTML files, this is wrong.

Denis, keywords not filtering.
'''
 

def timefix(str_time):
    # this time only has year, so default to Jan. 1
    if str_time == "Varies by indicator":return ''
    if "T" in str_time: raise Exception
    try:
        if len(str_time) == 4:
            return str(datetime.date(datetime(int(str_time),1,1)))
        elif len(str_time) == 7:
            return str(datetime.date(datetime(int(str_time.split("-")[0]),
                                                              int(str_time.split("-")[1]),1)))
        else:
            return str_time
    except ValueError:
        return ''
                
def time_coverage_fix(str_time1,str_time2):
    # Check to see if the start time and end time are different formats
    if len(str_time2) != len(str_time1):
        # make end time equal to start time
        return (str_time1, str_time1)
    else:
        return (str_time1, str_time2)
            

class Resource():
    """
    A generic resource class that can be extended to hold conversion and validation logic for each field
    
    """

    def __init__(self,language,url,format):      
        self.language=language
        self.url=url
        self.format=format
        
        
class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
    
      
