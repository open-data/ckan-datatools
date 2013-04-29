import lxml
import sys
import pickle
from collections import Counter
from pprint import pprint
import common
from ckanext.canada.metadata_schema import schema_description

class Resource:
    """
    A resource has the following fields:
    
    'url':
    'format':
    'resource_type': 'Dataset',
    'language':'English | Anglais'
                   
    """
    
    
    def __init__(self,url, format, resource_type='Dataset'):
        self.url=url
        self.format=format
        self.resource_type=resource_type

    def set_langauge(self,language):
        self.language=language
        
    def json(self):
        pass
    
class PilotRecord:
    
    """
    A pilot record can have the following atttributes or states:
        raw; the raw XML data from the pilot dump
        id
        title_en
        title_fr
        language__
        language
        title_language_indicator
        sibling 
        merged 
        states =[good,bad,questionable,merged]
        
        Keep this record simple at the base level, don't put a lot 
        of logic in it.  It should simply mirror the data that's in the 
        Pilot XML 

    """
    lang_marker_cnt = Counter()
    bad = open('badrecords.xml','w')
    def __init__(self,node):
        
        #This is required so it can be pickled
        #self.raw = lxml.etree.tostring(node)
        self.node = node
        self.title=''
        self.language=''
        self.resources=[]
        try:
            


            self.id = node.xpath("FORM[NAME='thisformid']/A/text()")[0]
            
            #[0].lower()
        except IndexError as ie: #Just in case there is no ID
            #print lxml.etree.tostring(node)
            # log this as a broken record and move on
#            self.bad.write(lxml.etree.tostring(node))
#            self.bad.write("\n")
            '''This class needs to know that it can't create itself 
                without an id, and alert the caller 
            '''
#            #print ">>>", ie, lxml.etree.tostring(self.node)
#            e = Exception()
#            e.id = None
#            e.type = 'MissingID'
#            e.message = "FORM[NAME='thisformid']/A/text() failed to find a value for this RECORD node, so I can't be instantiated."
#            e.node = node
            print "failed to get an id"

            
            #raise e
        try:
            ''' Set resources first '''
            self._title(node.xpath("FORM[NAME='title_en']/A/text()")) 
            self._resources(node)
                
                
            
            self._title_fra(node.xpath("FORM[NAME='title_fr']/A/text()"))
            self._language(node.xpath("FORM[NAME='language__']/A/text()"))
        
        except Exception as e: 
            print "Error setting field values" 
            print e
            raise
        '''
        self.__title(node.xpath("FORM[NAME='title_en']/A/text()"))
        self.__title(node.xpath("FORM[NAME='title_en']/A/text()"))
        self.__title(node.xpath("FORM[NAME='title_en']/A/text()"))
        self.__title(node.xpath("FORM[NAME='title_en']/A/text()"))
        self.__title(node.xpath("FORM[NAME='title_en']/A/text()"))
        self.__title(node.xpath("FORM[NAME='title_en']/A/text()"))
        self.__title(node.xpath("FORM[NAME='title_en']/A/text()"))
        self.__title(node.xpath("FORM[NAME='title_en']/A/text()"))
        self.__title(node.xpath("FORM[NAME='title_en']/A/text()"))
        self.__title(node.xpath("FORM[NAME='title_en']/A/text()"))
        '''   
    def _resources(self,node):
        
        dataset_links=['dataset_link_en_%d' % n for n in range(1,5)]
        for i, dl in enumerate(dataset_links):
            try:
                link = node.xpath("FORM[NAME='%s']/A/text()" % dl)[0]
                format_path = "FORM[NAME='%s']/A/text()" % "dataset_format_%d" % (i+1)
                format_code = node.xpath(format_path)
                resource = Resource(link, format_code)
                self.resources.append(resource)
                
                
                '''
                If the dataset is not bi-lingual, then get the equivalent
                french resource. But for now set as is, and handle this later
                when the entire collection can be searched
                
                It may not possible to set langauge for a resource
                at the resource level
                
                
                '''

            except Exception as e:
                #print "ERROR ", e
                # gettin to here means no more resources, so break
                continue

    def _title(self,title): 
        try:
            self.title = title[0]
 
        except IndexError as e: 
            e.id = None
            e.type = "TitleError"
            e.message = "No english title exists for this RECORD node."
            e.node = self.node
            raise e
    def _title_fra(self,title): 
        #print title[0]
        try:
            self.title_fr = title[0]
 
        except IndexError as e: 
            e.id = None
            e.type = "FrenchTitleError"
            e.message = "No french title exists for this RECORD node."
            e.node = self.node
            raise e
    def _language(self,lang_element): 
        try:
            langcode = lang_element[0].split("|")[1]
            self.language = schema_description.dataset_field_by_id['language']['choices_by_pilot_uuid'][langcode]['key']
            
        except:
            "Langcode missing"
            
    def match(self, filter):
        '''Determine if this note matches the filter
        text. Return True if it matches, False otherwise.
        Search is case sensitive and matches both text and
        tags.'''
        return filter in self.title_en or filter in self.title_fr
    
    def language_in_title(self):
        language_markers=[' - English Version',
                          ' - French Version',
                          ' (in English)', 
                          ' (in French)',
                          ' (In English)', 
                          ' (In French)',
                          '(- English)', 
                          '(- French)',  
                          ' (English version)',
                          ' (French version)',
                          ' (English Version)',
                          ' (French Version)' ] 
        for marker in language_markers:
            if marker in self.title:
               
                return True
        return False
        
class PilotHoldings:
    
    '''Represent a collection of records that can be
       modified and searched.
       These holdings should be in memory or pickled so there is no need to
       read raw data while working the data
    '''
    cnt = Counter()
    number_of_records=0
    records = []

    def __init__(self):
        
        self.bilingual = []
        self.french = []
        self.english = []
        self.suspect =[]
        self.broken = [] #List of exceptions along with NODE that caused  the record to break.
           
    def add_record(self, node):
        '''Create a new record and add it to the list.'''
        try:
            record = PilotRecord(node)
            num_resources = str(len(record.resources))  
            self.cnt[num_resources]+=1
            self.records.append(record)
            if record.language_in_title() and record.language == u"Bilingual (English and French) | Bilingue (Anglais et Fran\u00e7ais)":
                print "Bi with marker", record.id
            elif record.language == u"Bilingual (English and French) | Bilingue (Anglais et Fran\u00e7ais)":
                print "Just Bi", record.title
                
        except Exception as e:  
          
            print e
            raise      
            # One of the fields in the Record could not be found on Create
            #self.cnt[e.type]+=1 
            # Is This is where logging should take place
            #raise e IF YOU WANT THIS TO BUBBLE UP
            self.broken.append(e)

    def random_sample(self):
        for x in range(100,200):
            pass
            #print self.records[x]
            #pickle.dump(self.records, open("pilot.p", "wp"))
         
    def modify_record(self, record_id, memo):
        '''Find the record with the given id and change its
           memo to the given value.
        '''
        for record in self.records:
            if record.id == record_id:
                record.memo = memo
                break
               
    def modify_tags(self, note_id, tags):
        '''Find the record with the given id and change its
        tags to the given value.
        '''
        for record in self.records:
            if record.id == record_id:
                record.tags = tags
                break
    def find_french_record(self, filter_en):
        '''Find all records that match the given filter
           string.
        '''
        return [record for record in self.records if
            filter_en in record.title]
        
    def report(self, type):
        if type == 'full':
            print "Full Report"
            pprint(self.cnt.items())
    
        
    
        