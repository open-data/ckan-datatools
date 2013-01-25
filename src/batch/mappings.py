'''
Created on 2013-01-10

@author: jakoped

An easy place to read  and access fields mappings from pilot consisting of 
    pilot deparment _id, department acronym, department name
'''
from collections import namedtuple
import random

class Level:
    'A list field hierarchy types'
    PACKAGE = 'package'
    RESOURCE = 'resource'
    EXTRA = 'extra'


# I could also just make lists and then make sets out of them?

class Type:
    'A list of system requirements types'
    AUTO = 'ckan_auto'
    REQUIRED = 'ckan_required'
    OPTIONAL = 'ckan_optional'
    

Field = namedtuple("Field", "level ckan pilot schema type default example")
fields = [
          #Field(Level.PACKAGE,"id", "uniqueformid", "File Identifier", Type.OPTIONAL, "", "25576558-e95b-4496-bcd2-60cc34251888"),
          Field("package","name", "thisformid", "uri", Type.REQUIRED , "", "my-report"),
          Field("package","title", "title_en", "", "","",  ""),
          Field("package","version", "", "", "","",  ""),
          Field("package","author", "", "", "","",  ""),
          Field("package","author_email", "contact_email", "", "", "", ""),
          Field("package","maintainer", "", "", "", "", ""),
          Field("package","maintainer_email", "owner", "","",  "", ""),
          Field("package","notes", "", "", "", "", ""),
          Field("package","license_id", "", "", "", "", ""),
          Field("package","type", "", "", "", "", ""),
		  Field("package","state", "", "", "","",  ""),
	  	  Field("package","revision_id", "", "", "", "", ""),
	 	  Field("package","license", "", "", "", "", ""),
	 	  Field("package","isopen", "", "", "", "", ""),
	 	  Field("package","tags", "", "", "", "", ""),
	 	  Field("package","groups", "department", "", "", "", "['statcan']"),
	 	  Field("package","extras", "", "", "", "", ""),
	 	  Field("package","ratings_average", "", "", "", "", ""),
	 	  Field("package","ratings_count", "", "", "", "", ""),
	 	  Field("package","ckan_url", "", "", "", "", ""),
	 	  Field("package","relationships", "", "", "", "", ""),
	 	  Field("package","metadata_modified", "", "", "", "", ""),
	 	  Field("package","metadata_created", "", "", "", "", ""),
	 	  Field("package","notes_rendered", "", "", "", "", ""),
	 	  Field("package","tracking_summary", "", "", "", "", ""),
		 
		 
          Field("resource","url", "dataset_link_en_1", "", "","",""),
          Field("resource","name", "description_en", "", "","",  ""),
          Field("resource","format", "dataset_format_1", "", "","",  ""),
#          Field("resource","", "", "", "", "", ""),
#          Field("extra","", "", "", "","", "",""),
#          Field("extra","", "", "", "","", "",""),
#          

         ]

# give me all the ckan names that exists for pilot names that are not empty
ckan_pilot_common = { (f.ckan,f.pilot) for f in fields if (f.pilot != '' and f.level == 'package')}

ckan_package_fieldnames = { b.ckan for b in fields if b.level == 'package'}

common_resource_names = { (f.ckan,f.pilot) for f in fields if f.level == 'resource' }


''' Pythonistic Strategy Pattern  :) '''
def map_name(code):
    ''' Combine statcan with id '''
    return 'statcan' + code.lower().split('-')[0]
    
def _catalog_type():
    return  "strategically_named_catalog_type"

def _url():
    # corresponds with dataset_link_en_1
    return "http://www.statcan.gc.ca/cgi-bin/sum-som/fl/cstsaveascsv.cgi?filename=arts63a-fra.htm&amp;lan=fre"
    #resource['url'] = node.xpath("FORM['dataset_link_en_1']/A/text()")[0]
def _url_fra():
    # corresponds with dataset_link_en_1
    return "http://www.statcan.gc.ca/cgi-bin/sum-som/fl/cstsaveascsv.cgi?filename=arts63a-fra.htm&amp;lan=fre"
    #resource['url'] = node.xpath("FORM['dataset_link_en_1']/A/text()")[0]


def _dataset_link_fra():
    return  "http://www.statcan.gc.ca/tables-tableaux/sum-som/l02/cst01/index-fra.htm"

def _author():
    return  "Statistics Canada"

def _dataset_series():
    return  "http://www.statcan.gc.ca/tables-tableaux/sum-som/l02/cst01/index-fra.htm"

def _dataset_series_fra():
    return  "http://www.statcan.gc.ca/tables-tableaux/sum-som/l02/cst01/index-fra.htm"

def _issue_id():
    return  "9067-TRRF-909884"

def _tags():
    return  ['tag1', 'tag2', 'tag3', 'tag4']

def _topic():
    return  "Statistics Canada"

def map_subject(code):
    return "SUBJECT CODE "+ code

def map_geographic_region_name(code):
    return "GEOGRAPHIC REGION "+ code

def map_author(code):
    return  "stats-tab@statcan.gc.ca"

def random_id():
    return str(round(random.random() * 10000000)).split('.')[0]

code_mapping_strategies = {'CD9CE9D4-1AA3-40DB-AF1F-37B392656033': map_subject,
                           '671506AE-ED00-4DAA-B856-895A6169BB60': map_author,
                           'C3A1CE57-4E0F-43AF-82A1-9C634AD8E292': map_geographic_region_name,
                           } 

default_strategies = {'catalog_type': _catalog_type,
                      'url':_url,
                      'url_fra':_url,
                      'author':_author,
                      'author_email':_author,
                      'data_series_name':_dataset_series,
                      'data_series_name_fra':_dataset_series_fra,
                      'issue_identification':_issue_id,
                      'issue_identification_fra':_issue_id,
                      'tags':_tags,
                      'tags_fra':_tags,
                      'topic_category':_topic,
                      'xxxxxx':_author
                      } 




