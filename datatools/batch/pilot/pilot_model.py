import lxml
import sys
import pickle
from collections import Counter
from pprint import pprint
from ckanext.canada.metadata_schema import schema_description


class PilotResource():
    ''' Create a new Resource with empty values that can be set later 
        A resource cannot exist without a dataset parent; UUID 
        is required by construtor
    '''
    
    def  __init__(self,dict,type):
        self.fields=dict
        print dict
        self.type=type
      
        self._map()
    
    def _map(self):
        if 'dataset_link_en_' in self.type:
            try:
                self.fields['format']=schema_description.resource_field_by_id['format']['choices_by_pilot_uuid'][self.fields['format']]['key']
            except KeyError:
                self.fields['format']=''

            
        
    def display(self):
        pprint(self.fields)

class PilotRecord(object):
    ''' Create a new Record with empty values that can be set  later 
      
    '''
    
    fields={}
    schema_package_fields=[(ckan_name,pilot_name) for ckan_name, pilot_name, field in schema_description.dataset_all_fields()]
    def  __init__(self,node):
       self._process_xml(node)
       
    def _process_xml(self,node):
         try:
            self.id=node.xpath("FORM[NAME='thisformid']/A/text()")[0]
            self.resources=[]
            self._parse_fields(node)
       
         except:
            raise 
            self.id=None
           
    def _parse_fields(self,node):
        ''' package fields '''
        for ckan_name, pilot_name, field in schema_description.dataset_all_fields():
            if pilot_name:
                path = "FORM[NAME='%s']/A/text()"%pilot_name
                element = node.xpath(path)
                
                try:
                    # Deal with Pilot UUID CODES
                    value = element[0].strip()
                    if "|" in value:
                        split_value=value.split("|")[1]
                        self.fields[pilot_name] = field['choices_by_pilot_uuid'][split_value]['key']

                    else:
                        self.fields[pilot_name]=value
                except IndexError:
                    self.fields[pilot_name]=""
            else:
                # ckan_name / field does not belong at PilotRecord level.  Process in CanadaRecord
                pass
            ''' Grab data that is not defined in schema '''
            geo_lower_left = node.xpath("FORM[NAME='geo_lower_left']/A/text()")
            geo_upper_right = node.xpath("FORM[NAME='geo_upper_right']/A/text()") 
            if geo_lower_left and geo_upper_right and  geo_lower_left[0] != "N/A":
                print "GEO ", geo_upper_right, geo_lower_left       
                try:
                    left,bottom = geo_lower_left[0].split(" ")
                    right, top = geo_upper_right[0].split(" ")
                except ValueError:
                    '''  To catch values that have a dash that should perhaps be a minus  ['84 - 43'] ['41.5 - 141']  '''
                    left,bottom = geo_lower_left[0].replace(" - "," -").split(" -")
                    right, top = geo_upper_right[0].replace(" - "," -").split(" -")
                    
                coordinates = [[left, bottom], [left,top], [right, top], [right, bottom]]
                self.fields['spatial']= {'type': 'Polygon', 'coordinates': coordinates}  
            
            
        ''' resources'''
        for i in range(1,5):
            url = node.xpath("FORM[NAME='dataset_link_en_%d']/A/text()" % i)
            if url:
                resource_dict = {}
                resource_dict['url']=url[0]
                format = node.xpath("FORM[NAME='dataset_format_%d']/A/text()" % i)
                size = node.xpath("FORM[NAME='dataset_size_%d']/A/text()" % i)
                if format:resource_dict['format']=format[0].split("|")[1]
                self.resources.append(PilotResource(resource_dict,'dataset_link_en_'))
            else:               
                break
 
        extras=['supplementary_documentation_en',
                'supplementary_documentation_fr',
                'data_dictionary_fr',
                'dictionary_list:_en']
        ''' What about :
        data_dictionary_fr
        data_dictionary_en
        '''
        
        for extra in extras:
            url= node.xpath("FORM[NAME='%s']/A/text()"% extra)
            if url:
                resource_dict = {}
                resource_dict['url']=url[0]              
                self.resources.append(PilotResource(resource_dict,extra))

    def display(self,raw=False):
        print "-----------  Pilot <RECORD> -----------"
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
                print "Just Bilingual", record.title
                
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
    
        
    
        