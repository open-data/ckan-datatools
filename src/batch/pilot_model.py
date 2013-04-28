import lxml
import sys
import pickle
from collections import Counter
from pprint import pprint
import common


class Resource:
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
    def __init__(self,node):
        #This is required so it can be pickled
        #self.raw = lxml.etree.tostring(node)
        self.node = node
        try:
            
            self.id = node.xpath("FORM[NAME='thisformid']/A/text()")[0]
            
            #[0].lower()
        except IndexError: #Just in case there is no ID
            #print lxml.etree.tostring(node)
            # log this as a broken record and move on
            '''This class needs to know that it can't create itself 
                without an id, and alert the caller 
            '''
            e = Exception()
            e.id = None
            e.type = 'MissingID'
            e.message = "FORM[NAME='thisformid']/A/text() failed to find a value for this RECORD node, so I can't be instantiated."
            e.node = node
            raise e
            
            #raise e
        # With the broken ids out of the way, we can now do a lanuge sorting and other clean up work
        
        self.__title(node.xpath("FORM[NAME='title_en']/A/text()")) 
        #self.__title(node.xpath("FORM[NAME='title_fr']/A/text()"))
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
        self.__title(node.xpath("FORM[NAME='title_en']/A/text()"))
        '''   
            
    def __title(self,title): 
        
        try:
            self.title_en = title[0]
 
        except IndexError as e: 
            #e = Exception()
            e.id = None
            e.type = "TitleError"
            e.message = "No english title exists for this RECORD node."
            e.node = self.node
            raise e

class PilotHoldings:
    
    '''Represent a collection of records that can be
       modified and searched.
       These holdings should be in memory or pickled so there is no need to
       read raw data while working the data
    '''
    cnt = Counter()
    number_of_records=0
    def __init__(self):
        
        self.records = []
        self.bilingual = []
        self.french = []
        self.english = []
        self.suspect =[]
        self.broken = [] #List of exceptions along with NODE that caused  the record to break.
           
    def add_record(self, node):
        '''Create a new record and add it to the list.'''
        try:
            record = PilotRecord(node)
            self.records.append(record)
        except Exception as e:        
            # One of the fields in the Record could not be found on Create
            self.cnt[e.type]+=1 
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
    def search(self, filter):
        '''Find all records that match the given filter
           string.
        '''
        return [record for record in self.records if
            record.match(filter)]
    def report(self, type):
        if type == 'full':
            pprint(self.cnt.items())
    
        
    
        