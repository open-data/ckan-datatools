# coding=utf-8
'''
Created on 2013-01-10

@author: jakoped

This module is used for converting various items from in the pilot XML
'''
import sys
import logging
import simplejson as json
import time
from lxml import etree
from pprint import pprint
from datetime import date
import common
from common import XmlStreamReader
from ckanext.canada.metadata_schema import schema_description

# add filemode="w" to overwrite
logging.basicConfig(filename="/Users/peder/dev/goc/ckan-logs/pilot.log", level=logging.INFO)
pilot_file =  "/Users/peder/dev/OpenData/Pilot/OpenData_Feb13_extract-1.xml"  
output_file =  "/Users/peder/dev/OpenData/Pilot/april_15.jl"

pilot_frequency_list = {'annual':u'Annually | Annuel',
                        'quarterly':u'Quarterly | Trimestriel',
                        'monthly'  :u'Monthly | Mensuel', 
                        'bi-weekly':u'Fortnightly | Quinzomadaire',
                        'weekly':u'Weekly | Hebdomadaire',
                        'daily': u'Daily | Quotidien',
                        'hourly':u'Continual | Continue',
                        '':u'Unknown | Inconnu'}



# Don't generated this[(item['eng'],item['key']) for item in schema_description.dataset_field_by_id['maintenance_and_update_frequency']['choices']]

supplemental_info_fields=[
            'data_series_url_en',
            'dictionary_list:_en', # note: different than French
            'supplementary_documentation_en',
            'data_series_url_fr',
            'data_dictionary_fr',
            'supplementary_documentation_fr',
                            ]

language_markers=[
                    (' - English Version',' - French Version'),
                    (' (in English)', ' (in French)'),
                    (' (In English)', ' (In French)'),
                    ('(- English)', '(- French)'),  
                     (' (English version)',' (French version)'),
                    (' (English Version)',' (French Version)')
                    ]

def check_date(date):
    # Get rid of eg. 2008-06-26T08:30:00
    if "T" in date:
        date=date.split("T")[0]
            
    elif date=='':
        return date
    try:
        valid_date = time.strptime(date, '%Y-%m-%d')
        return date
    except ValueError:
        print 'Invalid date!', date
        return ''

class DoubleXmlStreamReader(XmlStreamReader):
    ''' 
        Sometimes inheritance IS usuful ;)
        Combines stream of english and french records into one RECORD  
        because we are streaming, we cannot use:
        zip(data.elements()[0::2], data.elements()[1::2])
        TODO: Consider using fast_iter:
        http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
        FIXME: Need to skip every other one for this to work with i%2, 
        and can no longer clear element in parent
    '''
    def combined_elements(self):
        for i,element in enumerate(self._iter_open()):
            if element.getprevious() is not None:
                if i%2==0:continue
                yield (element.getprevious(),element)  
                     
formats = schema_description.resource_field_by_id['format']['choices_by_pilot_uuid']

class TransformDouble:
    last_record_id=''
    def __init__(self,datafile,outfile):
        
        self.outfile = open(outfile,"w")
        self.data = DoubleXmlStreamReader("RECORD",datafile)
        
    def write_jl_file(self):
        for i,nodes in enumerate(self.data.combined_elements()):
            
            (node,node_fr) = nodes
            self._process_node(i,node,node_fr)
    def strip_title(self, title):
        language_markers = common.title_langauge_markers + common.title_langauge_markers_fra        
   
        for marker in language_markers:
            if marker in title:
                return title.replace(marker, '')
        
        return title
            
    def _process_node(self,count, node,node_fr):
        package_dict = {'resources': []}
        
        
        # Resource fields are not mapped in schema, so do them first 
        dataset_links=['dataset_link_en_%d' % n for n in range(1,7)]
        #if count>1000:sys.exit()
        for i, dl in enumerate(dataset_links):

            try:
               
                link1 = node.xpath("FORM[NAME='%s']/A/text()" % dl)
      
                if link1:
                    
                    link = link1[0]
                    format_path = "FORM[NAME='%s']/A/text()" % "dataset_format_%d" % (i+1)
                    format_code = node.xpath(format_path)
                    if format_code:
                        format_value = format_code[0].split("|")[1]
                        format = formats[format_value]['key']
                    else:
                        format = ''
                
                    link_fr = node_fr.xpath("FORM[NAME='%s']/A/text()" % dl)[0]
                    resource_dict = {'url':link, 'format':format, 'resource_type': 'Dataset','language':'English | Anglais'} 
                    resource_dict_fr = {'url':link_fr, 'format':format, 'resource_type': 'Dataset','language':'French | Fran\u00e7ais'} 
                    package_dict['resources'].append(resource_dict)
                    if link_fr != link:
                        package_dict['resources'].append(resource_dict_fr)
                else:
                    break
                
                
            except IndexError as e:
                print "RESOURCE ERROR ", e, link
                #This simply means that there is an empty link element, and it should be ignored
                pass
            except:
                raise
               
                      
        for ckan_name, pilot_name, field in schema_description.dataset_all_fields():
            print ckan_name, pilot_name
            try:
                     
                if ckan_name == "id":
                    package_dict['id'] =  str(node.xpath("FORM[NAME='thisformid']/A/text()")[0]).lower() 
                    
                    continue
                elif ckan_name in dataset_links:
                    continue
                elif ckan_name == 'name':
                    continue
                elif ckan_name== 'tags':
                    continue
                elif ckan_name == 'title':

                    t = node.xpath("FORM[NAME='title_en']/A/text()")[0]

                    package_dict['title'] =  self.strip_title(t)
                    if t == None: raise "No English Title", t
                    continue
                    
                elif ckan_name=='title_fra':

                    t_fr = node.xpath("FORM[NAME='title_fr']/A/text()")[0]
                    if t_fr == None: raise "No French Title", t_fr
                    package_dict['title_fra'] =  self.strip_title(t_fr)
                    continue
        
                value =''
                if pilot_name:
                    if pilot_name=="url_fra": 
                        print pilot_name
                    try: 
                        
                        result = node.xpath("FORM[NAME='%s']/A/text()" % pilot_name)
                        if result:
                            value  = result[0]
                        else: 
                            value =''
                  
                    except IndexError as e:
                        print "Some Form element Missing", e
     
                if "|" in value:
                    split_value = value.split("|")[1]
                    rval = field['choices_by_pilot_uuid'][split_value]
                    package_dict[ckan_name] = rval['key']
                    
                    if pilot_name == "department":
                        package_dict['owner_org'] = split_value
                    
                    if pilot_name in supplemental_info_fields:
                        print pilot_name
                else:
                    package_dict[ckan_name] = value
            except IndexError:  #when None, eg. same as elif pilot_name is None:
               package_dict[ckan_name] = ''

               
               continue
               #print count, "INDEX ERROR ", ckan_name, pilot_name,package_dict[pilot_name]
               
            except KeyError as e:
                print "KEY ERROR : ", ckan_name, pilot_name, e 
                package_dict[ckan_name] = ''
                continue
  
        
        # Filter out things that will not pass validatation
        if package_dict['geographic_region'] == "Canada  Canada":package_dict['geographic_region']=''
        package_dict['author_email'] =  'open-ouvert@tbs-sct.gc.ca'  
        package_dict['catalog_type'] = schema_description.dataset_field_by_id['catalog_type']['choices'][0]['key']
        package_dict['resource_type'] = 'file' #schema_description.dataset_field_by_id['resource_type']['choices']['file']
        #Override validation
        package_dict['validation_override']=True
        #Fix dates
        t = common.time_coverage_fix(package_dict['time_period_coverage_start'],package_dict['time_period_coverage_end'])
        package_dict['time_period_coverage_start'] = common.timefix(t[0])
        package_dict['time_period_coverage_end'] =  common.timefix(t[1])
        # Keywords Hack 
        print package_dict['time_period_coverage_start']
        print package_dict['time_period_coverage_end']
        
        key_eng = package_dict['keywords'].replace("/","-")
        key_fra = package_dict['keywords_fra'].replace("'","-").replace("/","-")
        package_dict['keywords'] = key_eng
        package_dict['keywords_fra'] = key_fra
       
        #print count, package_dict['id']
        self.outfile.write(json.dumps(package_dict) + "\n")



class TransformBilingual:
    
    last_id=''
    def __init__(self,datafile,outfile):
        
        self.outfile = open(outfile,"w")
        self.data = XmlStreamReader("RECORD",datafile)
        
    def write_jl_file(self):
        for i,node in enumerate(self.data.elements()):
            self._process_node(i,node)
            
    def strip_title(self, title):
        language_markers = common.title_langauge_markers + common.title_langauge_markers_fra        
   
        for marker in language_markers:
            if marker in title:
                return title.replace(marker, '')
        
        return title
            
    def _process_node(self,count, node):
        
        package_dict = {'resources': []}
        ''' Special fields that contain documents that must be added to resources, 
            but are not yet listed in the schema  
                        
                Pilot fields that should be stored as resource_type='doc' resources
                'data_series_url_en',
                'dictionary_list:_en', # note: different than French
                'supplementary_documentation_en',
 
                'data_series_url_fr',
                'data_dictionary_fr',
                'supplementary_documentation_fr',
        '''

        for sup_field in supplemental_info_fields:
            try:
                sup_value = node.xpath("FORM[NAME='%s']/A/text()" % sup_field)[0]
                #format = schema_description.resource_field_by_id['format']['choices_by_key']['html']['key']
                #print format
                # Create resource from this
                
                if "_en" in sup_field:
                    lang="eng; CAN"
                else:
                    lang = "fra; CAN"
                
                resource_dict = {'url':sup_value, 
                                         'format':'HTML',
                                         'resource_type': 'doc',
                                         'language':lang}
                
                package_dict['resources'].append(resource_dict)
            except:
                "EMPTY SUPPLEMENTAL VALUE"
        
        
       
        dataset_links=['dataset_link_en_%d' % n for n in range(1,7)]
        #if count>1000:sys.exit()
        for i, dl in enumerate(dataset_links):

            try:
               
                link = node.xpath("FORM[NAME='%s']/A/text()" % dl)[0]
                format=''
                

                try:
                    format_path = "FORM[NAME='%s']/A/text()" % "dataset_format_%d" % (i+1)
                    format_code = node.xpath(format_path)
                    format_uuid = format_code[0].split("|")[1]
                    format = schema_description.resource_field_by_id['format']['choices_by_pilot_uuid'][format_uuid]['key']
                except:
                    print "No Resource"
                    raise
                    
                resource_dict = {'url':link, 
                                         'format':format,
                                         'resource_type': 'file',
                                         'language':u'eng; CAN | fra; CAN'} 
                        
                package_dict['resources'].append(resource_dict)
    
            except IndexError as e:
                #  No Link element
                #This simply means that there is an empty link element, and it should be ignored
                pass
            except:
                raise
               
                      
        for ckan_name, pilot_name, field in schema_description.dataset_all_fields():
            
            
            try:
                     
                if ckan_name == "id":
                    package_dict['id'] =  str(node.xpath("FORM[NAME='thisformid']/A/text()")[0]).lower() 
                    
                    continue
                elif ckan_name in dataset_links:
                    continue
                elif ckan_name == 'name':
                    continue
                elif ckan_name== 'tags':
                    continue
                elif ckan_name == 'title':

                    t = node.xpath("FORM[NAME='title_en']/A/text()")[0]

                    package_dict['title'] =  self.strip_title(t)
                    if t == None: raise "No English Title", t
                    continue
                    
                elif ckan_name=='title_fra':
                    # Look for 
                    t_fr = node.xpath("FORM[NAME='title_fr']/A/text()")[0]
                    if t_fr == None: raise "No French Title", t_fr
                    package_dict['title_fra'] =  self.strip_title(t_fr)
                    continue
        
                value =''
                if pilot_name:
                    if pilot_name=="url_fra": 
                        print pilot_name
                    try: 
                        
                        result = node.xpath("FORM[NAME='%s']/A/text()" % pilot_name)
                        if result:
                            value  = result[0]
                        else: 
                            value =''
                  
                    except IndexError as e:
                        print "!!!!!!!!!", e
     
                if "|" in value:
                    split_value = value.split("|")[1]
                    rval = field['choices_by_pilot_uuid'][split_value]
                    package_dict[ckan_name] = rval['key']
                    
                    if pilot_name == "department":
                        package_dict['owner_org'] = split_value
                    
                else:
                    if pilot_name == 'frequency':
                        
                        package_dict['maintenance_and_update_frequency'] = pilot_frequency_list[value]
#                        print package_dict['maintenance_and_update_frequency']
#                        sys.exit()
                    else:

                        package_dict[ckan_name] = value
            except IndexError:  #when None, eg. same as elif pilot_name is None:
               package_dict[ckan_name] = ''

               
               continue
               #print count, "INDEX ERROR ", ckan_name, pilot_name,package_dict[pilot_name]
               
            except KeyError as e:
                print "KEY ERROR : ", ckan_name, pilot_name, e 
                package_dict[ckan_name] = ''
                continue
                

        # Filter out things that will not pass validatation
        if package_dict['geographic_region'] == "Canada  Canada":package_dict['geographic_region']=''
        package_dict['author_email'] =  'open-ouvert@tbs-sct.gc.ca'  
        package_dict['catalog_type'] = schema_description.dataset_field_by_id['catalog_type']['choices'][0]['key']
        package_dict['resource_type'] = 'file' #schema_description.dataset_field_by_id['resource_type']['choices']['file']
        #Override validation
        #package_dict['validation_override']=True
        #Fix dates
        t = common.time_coverage_fix(package_dict['time_period_coverage_start'],package_dict['time_period_coverage_end'])
        package_dict['time_period_coverage_start'] =common.timefix(t[0])
        package_dict['time_period_coverage_end'] = common.timefix(t[1])
        package_dict['date_published'] = str(package_dict['date_published']).replace("/", "-")
        package_dict['time_period_coverage_start']=check_date(package_dict['time_period_coverage_start'])
        package_dict['time_period_coverage_end']=check_date(package_dict['time_period_coverage_end'])
        package_dict['date_published']=check_date(package_dict['date_published'])

        #if count>1200:sys.exit() 
        key_eng = package_dict['keywords'].replace("/","-")
        key_fra = package_dict['keywords_fra'].replace("'","-").replace("/","-")
        package_dict['keywords'] = key_eng
        package_dict['keywords_fra'] = key_fra
        
        #pprint(package_dict['title_fra'])
        #print count, package_dict['id']
        '''  TODO: CHECK FOR DUPLICATES '''
        try:
            # Quick hack her to deal with bug that caused duplicate lines in XML 
            if len(package_dict['resources']) !=0 and package_dict['id'] != self.last_id:     
                #print "Write", package_dict['id']  
                self.last_id=package_dict['id']  
                self.outfile.write(json.dumps(package_dict) + "\n")
                #print count,package_dict['title']
                #pprint(package_dict)
#                print json.dumps(package_dict)
#                sys.exit()
        except Exception as e: 
            print e
            print count, "Can't Write", package_dict['id']
            
            #pprint(package_dict)
            pass
class Transform:
    
    last_id=''
    def __init__(self):
        pass       
    def strip_title(self, title):
        language_markers = common.title_langauge_markers + common.title_langauge_markers_fra        
   
        for marker in language_markers:
            if marker in title:
                return title.replace(marker, '')
        
        return title
    
    def node_resources(self,node):   
        resources=[]
        ''' Special fields that contain documents that must be added to resources, 
            but are not yet listed in the schema  
                        
                Pilot fields that should be stored as resource_type='doc' resources
                'data_series_url_en',
                'dictionary_list:_en', # note: different than French
                'supplementary_documentation_en',
 
                'data_series_url_fr',
                'data_dictionary_fr',
                'supplementary_documentation_fr',
        '''

        for sup_field in supplemental_info_fields:
            try:
                sup_value = node.xpath("FORM[NAME='%s']/A/text()" % sup_field)[0]
                #format = schema_description.resource_field_by_id['format']['choices_by_key']['html']['key']
                #print format
                # Create resource from this
                
                if "_en" in sup_field:
                    lang="eng; CAN"
                else:
                    lang = "fra; CAN"
                
                resource_dict = {'url':sup_value, 
                                         'format':'HTML',
                                         'resource_type': 'doc',
                                         'language':lang}
                
                resources.append(resource_dict)
            except:
                "EMPTY SUPPLEMENTAL VALUE"
        
        
       
        dataset_links=['dataset_link_en_%d' % n for n in range(1,5)]
        #if count>1000:sys.exit()
        for i, dl in enumerate(dataset_links):

            try:
               
                link = node.xpath("FORM[NAME='%s']/A/text()" % dl)[0]
                format=''

                try:
                    format_path = "FORM[NAME='%s']/A/text()" % "dataset_format_%d" % (i+1)
                    format_code = node.xpath(format_path)
                    format_uuid = format_code[0].split("|")[1]
                    format = schema_description.resource_field_by_id['format']['choices_by_pilot_uuid'][format_uuid]['key']
                except:
                    
                    raise
                    
                resource_dict = {'url':link, 
                                         'format':format,
                                         'resource_type': 'file',
                                         'language':u'eng; CAN | fra; CAN'} 
                resources.append(resource_dict)
            except:
                pass
                #print "Log No Resources here"
                #raise  
            
        return resources
        
    def process_node(self,count, node):
        
        package_dict = {'resources': []}
        
        package_dict['resources']  = self.node_resources(node)
        #print package_dict['resources']
       
        for ckan_name, pilot_name, field in schema_description.dataset_all_fields():

            try:
                     
                if ckan_name == "id":
                    package_dict['id'] =  str(node.xpath("FORM[NAME='thisformid']/A/text()")[0]).lower() 
                    
                    continue
#                elif ckan_name in dataset_links:
#                    continue
                elif ckan_name == 'name':
                    continue
                elif ckan_name== 'tags':
                    continue
                elif ckan_name == 'title':

                    t = node.xpath("FORM[NAME='title_en']/A/text()")[0]

                    package_dict['title'] =  self.strip_title(t)
                    if t == None: raise "No English Title", t
                    continue
                    
                elif ckan_name=='title_fra':
                    # Look for 
                    t_fr = node.xpath("FORM[NAME='title_fr']/A/text()")[0]
                    if t_fr == None: raise "No French Title", t_fr
                    package_dict['title_fra'] =  self.strip_title(t_fr)
                    continue
        
                value =''
                if pilot_name:
                    if pilot_name=="url_fra": 
                        print pilot_name
                    try: 
                        
                        result = node.xpath("FORM[NAME='%s']/A/text()" % pilot_name)
                        if result:
                            value  = result[0]
                        else: 
                            value =''
                  
                    except IndexError as e:
                        print "!!!!!!!!!", e
     
                if "|" in value:
                    split_value = value.split("|")[1]
                    rval = field['choices_by_pilot_uuid'][split_value]
                    package_dict[ckan_name] = rval['key']
                    
                    if pilot_name == "department":
                        package_dict['owner_org'] = split_value
                    
                else:
                    if pilot_name == 'frequency':
                        
                        package_dict['maintenance_and_update_frequency'] = pilot_frequency_list[value]
#                        print package_dict['maintenance_and_update_frequency']
#                        sys.exit()
                    else:

                        package_dict[ckan_name] = value
            except IndexError:  #when None, eg. same as elif pilot_name is None:
               package_dict[ckan_name] = ''

               continue
               #print count, "INDEX ERROR ", ckan_name, pilot_name,package_dict[pilot_name]
               
            except KeyError as e:
                print "KEY ERROR : ", ckan_name, pilot_name, e 
                package_dict[ckan_name] = ''
                continue
                

        # Filter out things that will not pass validatation
        if package_dict['geographic_region'] == "Canada  Canada":package_dict['geographic_region']=''
        package_dict['author_email'] =  'open-ouvert@tbs-sct.gc.ca'  
        package_dict['catalog_type'] = schema_description.dataset_field_by_id['catalog_type']['choices'][0]['key']
        package_dict['resource_type'] = 'file' #schema_description.dataset_field_by_id['resource_type']['choices']['file']
        #Override validation
        package_dict['validation_override']=True
        #Fix dates
        t = common.time_coverage_fix(package_dict['time_period_coverage_start'],package_dict['time_period_coverage_end'])
        package_dict['time_period_coverage_start'] =common.timefix(t[0])
        package_dict['time_period_coverage_end'] = common.timefix(t[1])
        package_dict['date_published'] = str(package_dict['date_published']).replace("/", "-")
        package_dict['time_period_coverage_start']=check_date(package_dict['time_period_coverage_start'])
        package_dict['time_period_coverage_end']=check_date(package_dict['time_period_coverage_end'])
        package_dict['date_published']=check_date(package_dict['date_published'])
        #if count>1200:sys.exit()
        
        key_eng = package_dict['keywords'].replace("/","-")
        key_fra = package_dict['keywords_fra'].replace("'","-").replace("/","-")
        package_dict['keywords'] = key_eng
        package_dict['keywords_fra'] = key_fra        
        #pprint(package_dict['title_fra'])
        
        #print count,package_dict['title'], len(package_dict['resources'])
        return package_dict   

class TransformDelegator:
    def __init__(self):
        pass
    def process_singles(self,datafile,outfile):
        self.outfile = open(outfile,"w")
        self.data = XmlStreamReader("RECORD",datafile)
        for i,node in enumerate(self.data.elements()):
            pprint (Transform.process_node(i,node))
            sys.exit()
        
    def process_doubles(self, datafile, outfile):
        self.outfile = open(outfile,"w")
        self.data = DoubleXmlStreamReader("RECORD",datafile)
        #self.data = XmlStreamReader("RECORD",datafile)

        for i, pair in enumerate(self.data.combined_elements()):
            node_en = pair[0]
            node_fr = pair[1]
  

            #print i,node_en, node_fr
            package_en = Transform().process_node(i,node_en)
            if "Fiscal Reference Tables - October 2010 - Table 9" in package_en['title']:
                 print etree.tostring(node_fr)
                 print "STOP"
            package_fr = Transform().process_node(i,node_fr)
            
            
            print "--------"
            print package_en['title']
            print package_fr['title']
            
            
            # Transfer French Data to English Package
            for pack in  package_fr['resources']:
                if pack['format'] != "HTML":
                    package_en['resources'].append(pack)
            
            #print json.dumps(package_en)
            
            
            '''
            title_en_short = None
       
            for en,fr in language_markers:
                if en in package_en['title']:
                
                    title_en_short = package_en['title'].split(en)[0]
                    
                    #print title_en_short
          
                    break
            try:
                title_en_no_brackets=None
                if title_en_short == None: 
                    if " [" in package_en['title']:
                        title_en_no_brackets = package_en['title'].split(" [")[0]
                        print title_en_no_brackets
#                    print "---------- SKIPPING ------------"
#                    print package_en['title']
#                    print package_fr['title']
#                    continue
                if title_en_short or title_en_no_brackets in package_fr['title']:
                    print i, "Lets do some work"
    #                print "--------OK----------"
                    print package_en['title']
                    print package_fr['title']
                    print "---------------------------"
                    
                else: 
                    pass
#                print "--------NOT OK----------"
#                print package_en['title']
#                print package_fr['title']
            
            except:
                print "not sure what happened", package_en['title']
                raise
            '''
         
if __name__ == "__main__":

    #PilotReport(pilot_file).number_of_records()
    outputdir = '/Users/peder/dev/goc/LOAD'
    pilot_file =  "/Users/peder/dev/goc/OD_DatasetDump-0-partial.xml" 
    #matched_file = "/Users/peder/dev/goc/matched-pilot-records.xml"
    matched_file="/Users/peder/dev/goc/pilot-matched-{}.xml".format('2013-05-05')
    bi_file = "/Users/peder/temp/bilingual-pilot.xml"
    output_file =  "{}/pilot-{}.jl".format(outputdir,date.today()) 
    bi_output_file =  "{}/bilingual-pilot-records-{}.jl".format(outputdir,date.today()) 
    #Transform(matched_file,output_file).write_jl_file()
    #TransformBilingual(bi_file,bi_output_file).write_jl_file()
    TransformDelegator().process_doubles(matched_file,output_file)
    #Transform().structure()   
    #Transform().replace()
    #process_pilot_xml('data/tables_20120815.xml')
