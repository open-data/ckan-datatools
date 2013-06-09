#-*- coding:UTF-8 -*-
import os
import re
import sys
import time
from lxml import etree
from pprint import pprint
import simplejson as json
from datetime import datetime,date
from string import Template
from datatools.batch.common import XPather
from datatools.batch import common
from ckanext.canada.metadata_schema import schema_description as schema
from pilot_model import PilotRecord


class PilotRules:
    
    bilingual_markers =[(' - Bilingual version',' - version bilingue'),]

    agriculture_title_markers = ['D035 ','109 - ','075/081 - ','077/078/082 -', '060 ','060 - ', '031N', '101 - ', '072 - ','072 ',
                                 '073 ', '073 - ', '070 ','070 - ', '066 - ', '050P',  'A009E','A009A', '003 - ', '003 ', 
                                 '077/078/082 - ', '075/081 - ', 'D019M']

    pilot_frequency_list = {'annual':u'Annually | Annuel',
                        'quarterly':u'Quarterly | Trimestriel',
                        'monthly'  :u'Monthly | Mensuel', 
                        'bi-weekly':u'Fortnightly | Quinzomadaire',
                        'weekly':u'Weekly | Hebdomadaire',
                        'daily': u'Daily | Quotidien',
                        'hourly':u'Continual | Continue',
                        '':'Unknown | Inconnu'}
    
    agriculture_title_markers = ['D035 ',
                             '109 - ',
                             '075/081 - ',
                             '077/078/082 -', 
                             '060 ','060 - ', '031N', '101 - ', 
                             '072 - ','072 ',
                             '073 ', '073 - ', 
                             '070 ','070 - ', 
                             '066 - ', '050P', 
                             'A009E', 
                             'A009A', 
                             '003 - ', '003 ',  
                             '077/078/082 - ', 
                             '075/081 - ', 
                             'D019M']
    
    topicKeys = dict((item['eng'], item['key']) for item in schema.dataset_field_by_id['topic_category']['choices'])
    formatTypes=dict((item['eng'], item['key']) for item in schema.resource_field_by_id['format']['choices'])
    
    def fix_date(date):
        # Get rid of eg. 2008-06-26T08:30:00
        if "T" in date:
            date=date.split("T")[0]
        elif date == "Varies by indicator":
            return ''
    
        elif "00:00:00" in date:
            date=date.split('00:00:00')[0]
        try:
            valid_date = time.strptime(date, '%Y-%m-%d')
            return date
        except ValueError:
            #print 'Invalid date!', date
            return ''

        
    def region_fix(self):
        if package_dict['geographic_region'] == "Canada  Canada":package_dict['geographic_region']=''
        region = package_dict['geographic_region']
        package_dict['geographic_region'] = region.replace("Yukon Territory  Territoire du Yukon","Yukon  Yukon" )
        package_dict['author_email'] =  'open-ouvert@tbs-sct.gc.ca'  
        package_dict['catalog_type'] = schema_description.dataset_field_by_id['catalog_type']['choices'][0]['key']
        
    def time_coverage_fix(self,time):
    #Fix dates
        try:

            t = common.time_coverage_fix(package_dict['time_period_coverage_start'],package_dict['time_period_coverage_end'])
            package_dict['time_period_coverage_start'] =common.timefix(t[0])
            package_dict['time_period_coverage_end'] = common.timefix(t[1])
             
        except KeyError:
            ''' Times were never set '''
            package_dict['time_period_coverage_start'] ="1000-01-01"
            package_dict['time_period_coverage_end']  ="3000-01-01"
            
    def workflow_fix(self):
        if node.find("FLOWSTATUS").text == "pending":
            package_dict['portal_release_date']=''
            
    def reformat_date(date_string):
        try:
            timepoint = datetime.strptime(date_string.strip(), "%m/%d/%Y") 
        except ValueError:
            timepoint = datetime.strptime(date_string.strip(), "%Y/%m/%d")
        day = timepoint.date()
        return day.isoformat()

        if "/" in package_dict['date_modified']: package_dict['date_modified']=reformat_date(package_dict['date_modified'])
 
    def clean_keywords(self,keywords):
        keywords = keywords.replace("\n"," ").replace("/","-").replace("(","").replace(")","").replace(":","-").replace(u"´","'").replace(".","").split(",")
        words = [k.strip() for k in keywords if len(k)<100 and len(k)>1]
        
        for w in words:
            tagname_match = re.compile('[\w \'-.]*$', re.UNICODE)
            if not tagname_match.match(w):
                words.remove(w)
        if words:
            return ",".join(words)
        else:
            return ''

       
        
    def title(self,title,department):
        if department=='aafc-aac':
            for marker in self.agriculture_title_markers:
                if marker in title:
                    title = title.split(marker)[1].lstrip(" ")

        for marker in common.language_markers:

            title = title.split(marker[0])[0]
            title = title.split(marker[1])[0]
        
        for marker in common.language_markers_fra:
            title = title.split(marker)[0]

        return title
        
    def geo_region(self,region):
        if region == "Canada  Canada": 
            return  ""
        else:
            return region
        
    def  format_date(self, date):  
        # Get rid of eg. 2008-06-26T08:30:00
        self.date = date
        if "T" in self.date:
            self.date=date.split("T")[0]
        elif self.date == "Varies by indicator":
            return ''
    
        elif "00:00:00" in self.date:
            self.date=date.split('00:00:00')[0]
            
        elif self.date == "Every 5-10 minutes":
           return ''
        try:
            if ", " in self.date:
                self.valid_date = datetime.strptime(self.date, "%B %d,  %Y")
            elif "/" in self.date:
                self.valid_date = datetime.strptime(self.date, "%Y/%m/%d")
            elif len(date)==4:
                self.valid_date = datetime.strptime(self.date, "%Y")
            else:
                self.valid_date = datetime.strptime(self.date, '%Y-%m-%d')           

            return str(self.valid_date.date())
        except ValueError:
            return ''
    

    def get_format(self,resource,department):
        format = resource.fields['format']
        if department =='hc-sc' and resource.type == 'file': format='TXT'
        if resource.fields['format'] not in self.formatTypes:
            return self.formatTypes['Other']
        else:
            return self.formatTypes[format]
        
    def get_topic_category(self,topic_name):
        try:
            topic = self.topicKeys[topic_name]
        except KeyError:
            topic =''
        
class CkanResource:
    
    langmap={'Bilingual':'eng; CAN | fra; CAN',
             'English':'eng; CAN',
             'French':'fra; CAN',
                  }
    def __init__(self,pilot):

        self.fields={}
        url = pilot.fields['url'].strip()
        if url.startswith('http://registry.data.gc.ca/commonwebsol'):
            url = url.replace('registry.data.gc.ca', 'data.gc.ca')
            url = url.split('|')[0]
        self.fields['url'] = url
        self._resource_type(pilot)
    
    def _resource_type(self, pilot):

        if 'dataset_link_en_' in pilot.type:
            self.fields['resource_type']='file'
            self.fields['name']='Dataset'
            self.fields['name_fra']='Ensemble de données'
            self.fields['format']=pilot.fields['format']
            self.fields['language']=self.langmap[pilot.fields['language']]       
            
        elif 'dictionary_list:_en' in pilot.type:
            self.fields['resource_type']='doc'
            self.fields['name']='Data Dictionary'
            self.fields['name_fra']='Dictionaire de données'
            self.fields['format']='HTML'
            self.fields['language']='eng; CAN'
            
        elif 'dictionary_list_fr' in pilot.type:
            self.fields['resource_type']='doc'
            self.fields['name']='Data Dictionary'
            self.fields['name_fra']='Dictionaire de données'
            self.fields['format']='HTML'
            self.fields['language']="fra; CAN"
                 
        elif 'supplementary_documentation_en' in pilot.type:
            self.fields['resource_type']='doc'
            self.fields['name']='Supporting Documentation'
            self.fields['name_fra']='Documentation de Soutien'
            self.fields['format']='HTML'
            self.fields['language']='eng; CAN'
            
        elif 'supplementary_documentation_fr' in pilot.type:
            self.fields['resource_type']='doc'
            self.fields['name']='Supporting Documentation'
            self.fields['name_fra']='Documentation de Soutien'
            self.fields['format']='HTML'
            self.fields['language']="fra; CAN"
            
class CanadaRecord:
    ''' 
    RESOURCE:
        1 name
        2 name_fra
        3 resource_type
        4 url
        5 size
        6 format
        7 language
    DATASET:
        1 id
        2 owner_org
        3 title
        4 title_fra
        5 notes
        6 notes_fra
        7 catalog_type
        8 subject
        9 topic_category
        10 keywords
        11 keywords_fra
        12 license_id
        13 geographic_region
        14 spatial
        15 spatial_representation_type
        16 presentation_form
        17 browse_graphic_url
        18 date_published
        19 date_modified
        20 maintenance_and_update_frequency
        21 data_series_name
        22 data_series_name_fra
        23 data_series_issue_identification
        24 data_series_issue_identification_fra
        25 digital_object_identifier
        26 time_period_coverage_start
        27 time_period_coverage_end
        28 url
        29 url_fra
        30 endpoint_url
        31 endpoint_url_fra
        32 ready_to_publish
        33 portal_release_date
    '''
    
    rules = PilotRules()
    
    def __init__(self,pilotrecord):

        self.id=pilotrecord.id.lower()
        self.package_dict={'resources':[]}
        self.data_identification(pilotrecord.fields)
        self.time_and_space(pilotrecord.fields)
        self.bilingual(pilotrecord.fields)
        self.resources(pilotrecord.resources)
        
    def data_identification(self,pilot):
        #8 of 33
        self.package_dict['id']=self.id
        self.package_dict['owner_org']=pilot['department'] 
        self.package_dict['topic_category']=self.rules.get_topic_category(pilot['category'])
        self.package_dict['subject']=''
        self.package_dict['catalog_type']=''
        self.package_dict['license_id']="ca-ogl-lgo"
        self.package_dict['presentation_form']=''
        self.package_dict['browse_graphic_url']=''
        self.package_dict['digital_object_identifier']=''

    def time_and_space(self, pilot):
        #10 if 33
        self.package_dict['date_published']=self.rules.format_date(pilot['date_released'])
        self.package_dict['date_modified']=self.rules.format_date(pilot['date_updated'])
        self.package_dict['maintenance_and_update_frequency']=self.rules.pilot_frequency_list[pilot['frequency']]
        self.package_dict['portal_release_date']='2013-06-01'
        self.package_dict['ready_to_publish']=True
        t = common.time_coverage_fix(pilot['time_period_start'],pilot['time_period_end'])
#        if t[0] or t[1]:
#            print "-----o------"
#            print pilot['time_period_start'],pilot['time_period_end']
#            print t
#            print self.rules.format_date(t[0]),self.rules.format_date(t[1])
#            print "-------d--------"
        #package_dict['time_period_coverage_start'] =common.timefix()
        #package_dict['time_period_coverage_end'] = common.timefix(t[1])
        self.package_dict['time_period_coverage_start']=self.rules.format_date(t[0])
        self.package_dict['time_period_coverage_end']=self.rules.format_date(t[1])
        self.package_dict['geographic_region']=self.rules.geo_region(pilot['Geographic_Region_Name'])
        self.package_dict['spatial']=''
        self.package_dict['spatial_representation_type']=''

    def bilingual(self,pilot):
        #14 of 33
        self.package_dict['data_series_name']=''
        self.package_dict['data_series_name_fra']=''
        self.package_dict['data_series_issue_identification']=''
        self.package_dict['data_series_issue_identification_fra']=''
        #package_dict['endpoint_url']='http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/'
        #package_dict['endpoint_url_fra']='http://geogratis.gc.ca/api/fr/nrcan-rncan/ess-sst/'
        self.package_dict['url']=pilot['program_page_en']
        self.package_dict['url_fra']=pilot['program_url_fr']
        self.package_dict['keywords']=self.rules.clean_keywords(pilot['keywords_en'])
        self.package_dict['keywords_fra']=self.rules.clean_keywords(pilot['keywords_fr'])
        self.package_dict['notes']=pilot['description_en']
        self.package_dict['notes_fra'] =pilot['description_fr']
        self.package_dict['title'] = self.rules.title(pilot['title_en'],pilot['department'])
        self.package_dict['title_fra'] = self.rules.title(pilot['title_fr'],pilot['department'])
              
    def resources(self,pilot_resources):
    
        for resource in pilot_resources:
            self.package_dict['resources'].append(CkanResource(resource).fields)
            
    def check_structure(dict):
        fields =  [ckan for ckan,pilot,field in schema.dataset_all_fields() if field['type'] not in [u'fixed',u'calculated']] 
        mandatory = [ckan for ckan,pilot,field in schema.dataset_all_fields() if field['mandatory'] == u'all']  
        fields.append('resources')  
        fields.append('validation_override')     
        missing_fields = set(dict.iterkeys()).symmetric_difference(set(fields)) 
        
        mandatory_fields = set(mandatory).intersection(set(fields))
        print "Missing Mandatory Fields", missing_fields.intersection(mandatory_fields)
        print "Missing Values ", [key for key,value in dict.items() if value=='MISSING']
        print "------------- Details ---------------"
        print "Fields Missing from Package_dict"
        pprint(list(missing_fields))
        
        print "Mandatory Fields that are not fixed or calculated"
        pprint(mandatory_fields)
   
    def display(self):
        print "------------  Canada Package ------------"
        pprint(self.package_dict)
  
  
''' Exclude CANSIM Records '''
exclude_record_patterns=['www20.statcan.gc.ca/tables-tableaux/cansim/csv',
              'www.statcan.gc.ca/cgi-bin/sum-som',
              'www12.statcan.gc.ca/census-recensement/2011/geo',
              'geodepot.statcan.gc.ca']     
  
def process_matched(infile, outfile): 
    jlfile = open(outfile,"w")
    tree = etree.parse(infile)
    root = tree.getroot()


    def combined_elements(root):
        for i,element in enumerate(root):
            if element.getprevious() is not None:
                if i%2==0:continue
                yield (element.getprevious(),element)   
                     
    for i,node in enumerate(combined_elements(root)):
         
        en_record = PilotRecord(node[0])
        fr_record = PilotRecord(node[1])

        '''Transfer french data resources to english record
           If there is a duplicated, assume that it's bilingual
           For example: 
           http://www20.statcan.gc.ca/tables-tableaux/cansim/csv/03030024-eng.zip
           http://www20.statcan.gc.ca/tables-tableaux/cansim/sdmx/03030024.zip
           This is a hack
        '''
        en_resources = dict((r.fields['url'],r) for r in en_record.resources)
        for resource in fr_record.resources:
            if resource.type == "dataset_link_en_":
                if resource.fields['url'] in en_resources.keys():
                    en_resources[resource.fields['url']].fields['language']="Bilingual"
                    
                else:
                    en_record.resources.append(resource)

        
        include_record=True
        for resource in en_record.resources:
            if resource.type == 'dataset_link_en_':
                for p in exclude_record_patterns:
                    if p in resource.fields['url']:
                        include_record=False  
        # Create CkanRecord
        if include_record:
            crecord = CanadaRecord(en_record)
            crecord.package_dict['validation_override']=True

            if i > 0 and (i % 100) == 0: print i 
            jlfile.write(json.dumps(crecord.package_dict) + "\n")  
   
def process_bilingual(infile, outfile): 
    jlfile = open(outfile,"w")
    tree = etree.parse(infile)
    root = tree.getroot()

    precords=[]
        
    for i,node in enumerate(root):
        
        precord = PilotRecord(node)
        
        include_record=True
        for resource in precord.resources:
            if resource.type == 'dataset_link_en_':
                for p in exclude_record_patterns:
                    if p in resource.fields['url']:
                        include_record=False  
        # Create CkanRecord
        if include_record:
            crecord = CanadaRecord(precord)
            crecord.package_dict['validation_override']=True

            jlfile.write(json.dumps(crecord.package_dict) + "\n")  

        if (i % 100) == 0: print i 
   
if __name__ == "__main__":
    matched_input =  "/Users/peder/dev/goc/LOAD/pilot-matched.xml"
    bilingual_input =  "/Users/peder/dev/goc/LOAD/pilot-bilingual.xml"
    sample_input=   "/Users/peder/dev/goc/LOAD/sample.xml"
    
    outputdir="/Users/peder/dev/goc/JL/"
    output_file_bilingual =  "{}/pilot-bilingual-{}.jl".format(outputdir,date.today()) 
    output_file_matched =  "{}/pilot-matched-{}.jl".format(outputdir,date.today()) 
    sample_output_file_bilingual =  "{}/pilot-sample-bilingual.jl".format(outputdir,date.today()) 
    sample_output_file_matched =  "{}/pilot-sample-mathed.jl".format(outputdir,date.today()) 
    print "Running"
    process_matched(matched_input,output_file_matched)
    process_bilingual(bilingual_input,output_file_bilingual)

    #process()