import lxml
import sys
import pickle
from collections import Counter
from pprint import pprint
from ckanext.canada.metadata_schema import schema_description


class RawPilotResource:
    ''' Create a new Resource with empty values that can be set later 
        A resource cannot exist without a dataset parent; UUID 
        is required by construtor
    '''
    
    def  __init__(self,url,type):
        self.url = url
        self.type=type
    
    def display(self):
        pprint (self.__dict__)
        '''
        print "\turl:", self.url
        print "\ttype:", self.type
        print "\tformat:", self.format
        print "\tsize:", self.size
        '''
class PilotRecord:
    ''' Create a new Record with empty values that can be set  later 
      
    '''
    
    fields={}
    schema_package_fields=[(ckan_name,pilot_name) for ckan_name, pilot_name, field in schema_description.dataset_all_fields()]
    def  __init__(self,node):

        try:
            self.id=node.xpath("FORM[NAME='thisformid']/A/text()")[0]
            self.resources=[]
            self._parse_xml(node)
            
        except:
            raise 
            self.id=None
            
    def _parse_xml(self,node):
        ''' package fields '''
        for ckan,pilot in self.schema_package_fields:
            if pilot:
                path = "FORM[NAME='%s']/A/text()"%pilot
                value = node.xpath(path)
                
                try:
                    self.fields[pilot]=value[0].strip()
                except IndexError:
                    self.fields[pilot]=""
            else:
                #Does not belong in this class
                pass
        ''' resources'''
        for i in range(1,5):
            url = node.xpath("FORM[NAME='dataset_link_en_%d']/A/text()" % i)
            if url:
                resource=RawPilotResource(url[0],'data')
                format = node.xpath("FORM[NAME='dataset_format_%d']/A/text()" % i)
                size = node.xpath("FORM[NAME='dataset_size_%d']/A/text()" % i)
                if format:resource.format=format[0]
                if size:resource.size=size[0]
                self.resources.append(resource)
            else:
                break
                
                
        extras=['supplementary_documentation_en',
                'supplementary_documentation_fr',
                'data_dictionary']
        
        for extra in extras:
            url= node.xpath("FORM[NAME='%s']/A/text()"% extra)
            if url:
                resource = RawPilotResource(url[0],extra)

    
    def display(self,raw=False):
        print "DATASET"
        for key,value in sorted(self.fields.items()):
            if raw:
                
                print "{}:{}".format(key,repr(value))
            else:
                print "{}:{}".format(key,value.strip())
        print len(self.resources), "RESOURCES"
        for resource in self.resources:
            
            resource.display()

        
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
    
        
    
        