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

#remove leading spaces from URLs

pilot_frequency_list = {'annual':u'Annually | Annuel',
                        'quarterly':u'Quarterly | Trimestriel',
                        'monthly'  :u'Monthly | Mensuel', 
                        'bi-weekly':u'Fortnightly | Quinzomadaire',
                        'weekly':u'Weekly | Hebdomadaire',
                        'daily': u'Daily | Quotidien',
                        'hourly':u'Continual | Continue',
                        '':'Unknown | Inconnu'}


# Don't generated this[(item['eng'],item['key']) for item in schema_description.dataset_field_by_id['maintenance_and_update_frequency']['choices']]

supplemental_info_fields=[
            #'data_series_url_en',
            'dictionary_list:_en', # note: different than French
            'supplementary_documentation_en',
            #'data_series_url_fr',
            'data_dictionary_fr',
            'supplementary_documentation_fr',
                            ]

bilingual_markers =[
                    (' - Bilingual version',
                     ' - version bilingue'),
                    ]

agriculture_title_markers = ['D035 ',
                             '109 - ',
                             '075/081 - ',
                             '077/078/082 -', 
                             '060','060 - ', '031N', '101 - ', 
                             '072 - ','072 ',
                             '073 ', '073 - ', 
                             '070','070 - ', 
                             '066 - ', '050P', 
                             'A009E', 
                             'A009A', 
                             '003 - ', '003',  
                             '077/078/082 - ', 
                             '075/081 - ', 
                             'D019M']

validation_override=True

def check_date(date):
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
        
        
        DANGER DANGER : This seems to be broken!
    '''
    def combined_elements(self):
        for i,element in enumerate(self._iter_open()):
            if element.getprevious() is not None:
                if i%2==0:continue
                yield (element.getprevious(),element)  
                     
formats = schema_description.resource_field_by_id['format']['choices_by_pilot_uuid']

class Transform:
    
    last_id=''
    def __init__(self):

        pass       
    def strip_title(self, title):
        if " - Bilingual version" in title:
            title.replace(" - Bilingual version","")
        if " - version bilingue" in title:
            title.replace(" - version bilingue","")    
        for marker in common.language_markers:
            if marker[0] in title:
                return title.split(marker[0])[0]
            elif marker[1] in title:
                return title.split(marker[1])[0]
        
        
        return title
    
    def node_resources(self,node, language):   
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
                                         'name':'Data Dictionary',
                                         'name_fra':'Dictionaire de données',
                                         'language':lang}
                
                resources.append(resource_dict)
            except:
                pass
                #print "EMPTY SUPPLEMENTAL VALUE"

        dataset_links=['dataset_link_en_%d' % n for n in range(1,5)]
        #if count>1000:sys.exit()
        for i, dl in enumerate(dataset_links):
            '''
            supplementary_documentation_en
            supplementary_documentation_fr
            data_dictionary
            number_datasets
            dataset_link_en_6
            dataset_size_en_6
            dataset_format_6
            '''
            
            try:
               
                link = node.xpath("FORM[NAME='%s']/A/text()" % dl)
                if link==[]:
                    continue
                else:
                    link = link[0]
                format=''
                #language = u'eng; CAN | fra; CAN'

                try:
                    format_path = "FORM[NAME='%s']/A/text()" % "dataset_format_%d" % (i+1)
                    format_code = node.xpath(format_path)
                    if format_code:
                        format_uuid = format_code[0].split("|")[1]
                        format = schema_description.resource_field_by_id['format']['choices_by_pilot_uuid'][format_uuid]['key']
                    else:
                        format = 'other'
                    
                except IndexError:
                    pass
                    #raise
                except:
                    raise
  
           
                resource_dict = {'url':link, 
                                         'format':format,
                                         'resource_type': 'file',
                                         'name':'Dataset',
                                         'name_fra':'Ensemble de données',
                                         'language':language} 
                resources.append(resource_dict)
            except:
                pass
                #print "Log No Resources here"
                raise  
            
        return resources
        
    def process_node(self,count, node, language):

        try:
            id = str(node.xpath("FORM[NAME='thisformid']/A/text()")[0]).lower() 
        except:
            print "======NO ID=========", node.xpath("DC.TITLE")[0].text
            #print etree.tostring(node)
            #sys.exit()
        # look for geographic bounding boxes
        if node.xpath("FORM[NAME='thisformid']/A/text()")[0] == 'F34DCB32-4845-4E88-B125-5AC03C6E4A7F':
            print "STOP"
        try:
            
            geo_lower_left = node.xpath("FORM[NAME='geo_lower_left']/A/text()")
            geo_upper_right = node.xpath("FORM[NAME='geo_upper_right']/A/text()") 
            print geo_lower_left
            if geo_lower_left:
                 print ">>>>>>>",id, geo_lower_left
                 sys.exit()
        except:
            print "NO GEO"
            
            
        if count > 10000:sys.exit()
        package_dict = {'resources': []}
        
        package_dict['resources']  = self.node_resources(node,language)


        for ckan_name, pilot_name, field in schema_description.dataset_all_fields():
          
            try:
                     
                if ckan_name == "id":
                    package_dict['id'] =  str(node.xpath("FORM[NAME='thisformid']/A/text()")[0]).lower() 
                    
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
                    # Filter out -version anglaise etc
                    for marker in common.language_markers_fra:
                        if marker in t_fr:
                            package_dict['title_fra'] = t_fr.split(marker)[0]
                            break
                        package_dict['title_fra'] =  t_fr
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
                            print e
     
                if "|" in value:
                    split_value = value.split("|")[1]
                    rval = field['choices_by_pilot_uuid'][split_value]
                    package_dict[ckan_name] = rval['key']
                    
                    if pilot_name == "department":
                        package_dict['owner_org'] = field['choices_by_pilot_uuid'][split_value]['key']
                        
                else:
                    if pilot_name == 'frequency':
                        if value:
                            package_dict['maintenance_and_update_frequency'] = pilot_frequency_list[value]
                        else:
                            package_dict['maintenance_and_update_frequency'] = pilot_frequency_list['']
                        continue
                    else:

                        package_dict[ckan_name] = value
            except IndexError:  #when None, eg. same as elif pilot_name is None:
               package_dict[ckan_name] = ''

               continue
               print count, "INDEX ERROR ", ckan_name, pilot_name,package_dict[pilot_name]
               
            except KeyError as e:
                print "KEY ERROR : ", ckan_name, pilot_name, e 
                package_dict[ckan_name] = ''
                continue
                

        # Filter out things that will not pass validatation
        if package_dict['geographic_region'] == "Canada  Canada":package_dict['geographic_region']=''
        package_dict['author_email'] =  'open-ouvert@tbs-sct.gc.ca'  
        package_dict['catalog_type'] = schema_description.dataset_field_by_id['catalog_type']['choices'][0]['key']
        #Override validation
        package_dict['validation_override']=validation_override
        #Fix dates
        try:

            t = common.time_coverage_fix(package_dict['time_period_coverage_start'],package_dict['time_period_coverage_end'])
           
            package_dict['time_period_coverage_start'] =common.timefix(t[0])
            package_dict['time_period_coverage_end'] = common.timefix(t[1])
             
        except KeyError:
            ''' Times were never set '''
            package_dict['time_period_coverage_start'] ="1000-01-01"
            package_dict['time_period_coverage_end']  ="3000-01-01"
            
      
        package_dict['date_published'] = str(package_dict['date_published']).replace("/", "-")
        package_dict['time_period_coverage_start']=check_date(package_dict['time_period_coverage_start'])
        package_dict['time_period_coverage_end']=check_date(package_dict['time_period_coverage_end'])
        package_dict['date_published']=check_date(package_dict['date_published'])
        package_dict['license_id']='ca-ogl-lgo'
        #if count>1200:sys.exit()
        
        key_eng = package_dict['keywords'].replace("\n"," ").replace("/","-").replace("(","").replace(")","").split(",")
        key_fra = package_dict['keywords_fra'].replace("\n"," ").replace("/","-").replace('"','').replace("(","").replace(")","").split(", ")
        package_dict['keywords'] = ",".join([k.strip() for k in key_eng if len(k)<100 and len(k)>1])
        package_dict['keywords_fra'] = ",".join([k.strip() for k in key_fra if len(k)<100 and len(k)>1])

        if package_dict['owner_org']=='aafc-aac':
            for marker in agriculture_title_markers:
                if marker in package_dict['title']:
                    new = package_dict['title'].split(marker)[1]
                    package_dict['title']=new.lstrip(" ")
                    break
                    
            for marker in agriculture_title_markers:
                if marker in package_dict['title_fra']:
                    new_fr = package_dict['title_fra'].split(marker)[1]
                    package_dict['title_fra']=new_fr.lstrip(" ")
                    break
                       
        if package_dict['owner_org']=='hc-sc':
            for resource in package_dict['resources']:
                if resource['resource_type']=='file':
                    resource['resource_type']='txt'   
                            
        #print count,package_dict['title'], len(package_dict['resources'])
        return package_dict   

class TransformDelegator:
    def __init__(self, outfile):
        self.outfile = open(outfile,"w")
     
    def process_singles(self,datafile):
        tree = etree.parse(datafile)
        root = tree.getroot()
        
        for i,node in enumerate(root):
            package = Transform().process_node(i,node,u"eng; CAN | fra; CAN")
            print "--- Bilingual -----", i
            print "TITLE", package['title']
            print "TITLE FR", package['title_fra']
            
            if not package['title']:
                print "########   NO TITLE ########",package['id']
                #print etree.tostring(node)
                #sys.exit()
            elif not package['owner_org']:
                print "############### NO ORGANIZATION ###########",package['id']
            elif not package['id']:
                print "############ NO ID ###########",package['id']
                #sys.exit()
                
            else:
                pass
                print i, "OK", package['id']
                self.outfile.write(json.dumps(package) + "\n")
               
        self.outfile.close()

    def combined_elements(self, root):
        for i,element in enumerate(root):
            if element.getprevious() is not None:
                if i%2==0:continue
                yield (element.getprevious(),element) 
        
    def process_doubles(self, datafile):
         tree = etree.parse(datafile)
         root = tree.getroot()

         for i,pair in enumerate(self.combined_elements(root)):

            node_en = pair[0]
            node_fr = pair[1]
     
            package_en = Transform().process_node(i,node_en, "eng; CAN")
            package_fr = Transform().process_node(i,node_fr,u"fra; CAN")

            # Transfer French Data to English Package
            for pack in  package_fr['resources']:
                if pack['format'] != "HTML":
                    package_en['resources'].append(pack)
            

            if package_en['resources'] == []:
                raise Exception

            if not package_en['owner_org']:
                print "############### NO ORGANIZATION ###########", package_en['id']
            
            elif not package_en['title']:
                print "############### NO TITLE ###########", package_en['id']
#                print pair[0]
#                print pair[1]

            elif not package_en['id']:
                "############ NO ID ###########",package_en['id']
                #sys.exit()
            else:
                print i, "OK",package_en['id']
                print package_en['title']
                print package_en['title_fra']
                
               
                self.outfile.write(json.dumps(package_en) + "\n")
     
   
if __name__ == "__main__":
    
    validation_override=True
    outputdir = '/Users/peder/dev/goc/LOAD'
    #matched_file="/Users/peder/dev/goc/pilot-matched.xml"
    matched_file="/Users/peder/dev/goc/LOAD/pilot-matched.xml"
    bi_file = "/Users/peder/temp/pilot-bilingual.xml"
    output_file =  "{}/pilot-{}.jl".format(outputdir,date.today()) 

    transform = TransformDelegator(output_file)
    print "PROCESSING MERGED FILES"
    transform.process_doubles(matched_file)
    print "PROCESSING BILINGUAL FILES"
    transform.process_singles(bi_file)

