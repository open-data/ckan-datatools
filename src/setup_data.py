#from ckanext.canada.metadata_schema import schema_description
#from ckanext.canada.metadata_schema import MetadataSchema
#import json
#from pprint import pprint
#import itertools
'''
For entering new groups at /rest/group   
                
'''
departments=[
{'name':'agriculture',
          'title':'Agriculture and Agri-Food Canada',
          'description':"Sample Departmental Description",
          'type':'group'},
{'name':'atlantic',
          'title':'Atlantic Canada Opportunities Agency',
          'description':'Explore the normal distribution with us',
          'type':'group'},
{'name':'cbsa',
          'title':'Canada Border Services Agency',
          'description':'Sample Departmental Description',
          'type':'group'},
{'name':'cra',
          'title':'Canada Revenue Agency',
          'description':"Sample Departmental Description",
          'type':'group'},
{'name':'cida',
          'title':'Canadian International Development Agency',
          'description':"Sample Departmental Description",
          'type':'group'},
{'name':'space',
          'title':'Canadian Space Agency',
          'description':"Sample Departmental Description",
          'type':'group'},
{'name':'finance',
          'title':'Department of Finance Canada',
          'description':"Sample Departmental Description",
          'type':'group'},
{'name':'nrcan',
          'title':'Department of Finance Canada',
          'description':'Sample Departmental Description',
          'type':'group'},
{'name':'oceans',
          'title':'Fisheries and Oceans Canada',
          'description':"Sample Departmental Description",
          'type':'group'},
{'name':'foreign',
          'title':'Foreign Affairs and International Trade Canada',
          'description':"Sample Departmental Description",
          'type':'group'},
{'name':'health',
          'title':'Health Canada',
          'description':"Sample Departmental Description",
          'type':'group'},
{'name':'industry',
          'title':'Industry Canada',
          'description':"Sample Departmental Description",
          'type':'group'},
{'name':'archives',
          'title':'Library and Archives Canada',
          'description':"Sample Departmental Description",
          'type':'group'},
{'name':'library',
          'title':'Library of Parliament',
          'description':"Sample Departmental Description",
          'type':'group'},
{'name':'defense',
          'title':'National Defence',
          'description':"Sample Departmental Description",
          'type':'group'},
{'name':'nrcan',
          'title':'Natural Resources Canada',
          'description':"Sample Departmental Description",
          'type':'group'},
{'name':'safety',
          'title':'Public Safety Canada',
          'description':"Sample Departmental Description",
          'type':'group'},
{'name':'pwgsc',
          'title':'Public Works and Government Services Canada',
          'description':"Sample Departmental Description",
          'type':'group'},
{'name':'statcan',
          'title':'Statistics Canada',
          'description':"Sample Departmental Description",
          'type':'group'},
{'name':'transport',
          'title':'Transport Canada',
          'description':"Sample Departmental Description",
          'type':'group'},
{'name':'tbs',
          'title':'Treasury Board of Canada Secretariat',
          'description':"Sample Departmental Description",
          'type':'group'}]



def data_type():
    '''
    Returns a package and/or resource that is
    
    1. The least amount required to be useful
    2. What is in the current metadata_schema 
    3. Maximum defualt ckan fields
    4. Ideal metadata_schema
    
    '''
    print schema_set

def post_departments(departments):
    for dept in departments:
        submit(dept,'group')
        #print "%s = %s" % (dept['name'],dept['title'])

def update_departments(departments):
    for dept in departments:
        print dept['name']
        update(dept,dept['name'],'group')
        
def add_data(package_items):
    for pack in package_items:
        update(pack,pack['name'],'package')





# Data
package_items = [
    {'name':'test-data-set1',
     'title':'Certified organic products, by province (2001 and 2006 Census of Agriculture)',
     'notes':'A description of Certified organic products, by province (2001 and 2006 Census of Agriculture)',
     'resources':[{'url':'http://www.dcsf.gov.uk/rsgateway/DB/SFR/s000859/SFR17_2009_tables.xls',
                  'format':'XLS',
                  'description':'December 2012 | http://www.statcan.gc.ca/hub/id/119-36345'},
                  {'url':'http://www.dcsf.gc.ca/rsgateway/DB/SFR/s000860/SFR17_2009_key.doc',
                  'format':'DOC',
                  'description':'http://www.statcan.gc.ca/hub/id/119-34565'}],
     'url':'http://www.dcsf.gc.ca/rsgateway/DB/SFR/s000859/index.shtml',
     'author':'Statcan Data Services Group',
     'author_email':'statistics@dcsf.gsi.gc.ca',
     'license':'ukcrown',
     'tags':'organic foods',
     'extras':{
        'external_reference':'DCSF-DCSF-0024',
        'date_released':'2012-07-30',
        'date_updated':'2012-07-30',
        'update_frequency':'annually',
        'geographic_granularity':'regional',
        'geographic_coverage':'100000: Canada',
        'department':'Department for Education',
        'published_by':'Department for Education [3]',
        'published_via':'',
        'temporal_granularity':'years',
        'temporal_coverage-from':'2008-6',
        'temporal_coverage-to':'2009-6',
        'mandate':'',
        'national_statistic':'yes',
        'precision':'Numbers to nearest 10, percentage to nearest whole number',
        'taxonomy_url':'',
        'agency':'',
        'import_source':'ONS-Jan-09',
        }
     },
    {'name':'weekly-fuel-prices',
     'title':'Weekly fuel prices',
     'notes':'Latest price as at start of week of unleaded fuel and diesel.',
     'resources':[{'url':'http://www.decc.gov.uk/assets/decc/statistics/source/prices/qep211.xls', 'format':'XLS', 'description':'Quarterly 23/2/12'}],
     'url':'http://www.decc.gc.ca/en/content/cms/statistics/source/prices/prices.aspx',
     'author':'DECC Energy Statistics Team',
     'author_email':'energy.stats@decc.gsi.gc.ca',
     'license':'ukcrown',
     'tags':'fuel prices',
     'extras':{
        'external_reference':'DECC-DECC-0001',
        'date_released':'2012-11-24',
        'date_updated':'2012-11-24',
        'update_frequency':'weekly',
        'geographic_granularity':'national',
        'geographic_coverage':'111100: Canada (Ontario, Quebec)',
        'department':'Department of Energy and Climate Change',
        'published_by':'Department of Energy and Climate Change [4]',
        'published_via':'',
         'mandate':'',
        'temporal_granularity':'weeks',
        'temporal_coverage-from':'2008-11-24',
        'temporal_coverage-to':'2009-11-24',
        'national_statistic':'no',
        'import_source':'DECC-Jan-09',
        }
     }
    ]

null = ''
true = 'true'
canada_test_package = {'maintainer': 'Peder Jakobsen',
         'maintainer_email': 'pjakobsen@gmail.com', 
         'id': '562a3b44-cc6f-45bd-80c1-96ab80a9e386', 
         'metadata_created': '2012-12-19T15:10:12.293000', 
         'relationships': [], 
         'metadata_modified': 
         '2012-12-19T15:10:12.293000', 
         'author': '', 
         'author_email': '', 
         'download_url': 'http://www.annakarenina.com/download/x=1&y=2', 
         'state': 'active', 
         'version': '0.7a', 
         'license_id': 
         'other-open', 
         'type': '', 
         'resources': [
               {'mimetype': '', 
                'resource_group_id': '7ad7dcdf-e7a5-4d68-b1b2-987b63963837', 
                'mimetype_inner': '', 
                'cache_url': '', 
                'hash': 'abc123', 
                'description': 'Full text. Needs escaping: " Umlaut: \\u00fc', 
                'cache_last_updated': '', 
                'url': 'http://www.annakarenina.com/download/x=1&y=2', 
                'format': 'plain text', 
                'tracking_summary': {'total': 0, 'recent': 0}, 
                'name': '', 
                'size_extra': '123', 
                'last_modified': '', 
                'created': '2012-12-19T10:10:12.583000', 
                'webstore_last_updated': '', 
                'position': 0, 'package_id': '562a3b44-cc6f-45bd-80c1-96ab80a9e386', 
                'webstore_url': '', 'id': 'fd49b9fe-139e-4387-9de9-4e5c6137c350', 
                'resource_type': '',
                 'size': ''}, 
               {'mimetype': '', 
                'resource_group_id': 
                '7ad7dcdf-e7a5-4d68-b1b2-987b63963837', 
                'mimetype_inner': '', 
                'cache_url': '', 
                'hash': 'def456', 
                'description': 'Index of the novel', 
                'cache_last_updated': '', 
                'url': 'http://www.annakarenina.com/index.json', 
                'format': 'json', 
                'tracking_summary': {'total': 0, 'recent': 0}, 
                'name': '', 
                'size_extra': '345', 
                'last_modified': '', 
                'created': '2012-12-19T10:10:12.583000', 
                'webstore_last_updated': '', 
                'position': 1, 
                'package_id': '562a3b44-cc6f-45bd-80c1-96ab80a9e386', 
                'webstore_url': '', 'id': 
                'c94c74f1-c14b-41c5-9362-aedc9e35c637', 
                'resource_type': '', 
                'size': ''}], 
                'tags': ['Flexible \\u30a1', 'russian', 'tolstoy'], 
                'tracking_summary': {'total': 0, 'recent': 0}, 
                'groups': ['david', 'roger'], 
                'name': 'annakarenina', 
                'isopen': 'true', 
                'license': 'Other (Open)', 
                'notes_rendered': '<p>Some test notes\n</p>\n\n<h3>A 3rd level heading</h3>\n<p><strong>Some bolded text.</strong>\n</p>\n<p><em>Some italicized text.</em>\n</p>\n<p>Foreign characters:\n   u with umlaut \\u00fc\n   66-style quote \\u201c\n   foreign word: th\\u00fcmb\n</p>\n<p>Needs escaping:\n   left arrow &lt;\n</p>\n<p><a href="http://ckan.net/" target="_blank" rel="nofollow">http://ckan.net/</a>\n</p>', 
                'url': 'http://www.annakarenina.com', 
                'notes': 'Some test notes\n\n### A 3rd level heading\n\n**Some bolded text.**\n\n*Some italicized text.*\n\nForeign characters:\nu with umlaut \\u00fc\n66-style quote \\u201c\nforeign word: th\\u00fcmb\n\nNeeds escaping:\nleft arrow <\n\n<http://ckan.net/>\n\n', 
                'license_title': 'Other (Open)', 'ratings_average': '', 
                'extras': {'genre': 'romantic novel', 'original media': 'book'}, 
                'ratings_count': 0, 'title': 'A Novel By Tolstoy', 
                'revision_id': 'c9433632-5798-4eca-b05d-ce30fa57c6ce'}


def metadata_sets():  
    package = canada_test_package.keys()
    one_resource= canada_test_package['resources'][0].keys()
    test_data_fields = (set(package) | set(one_resource))
    global test_data_set
    test_data_set = sorted(s.decode('utf8') for s in test_data_fields)     
    global schema_set
    schema_set = set(ckan_id
                     for ckan_id, ignore, field
                     in schema_description.fields_by_ckan_id(include_existing=True)
                     if field['existing'])
    print schema_set





# http://stackoverflow.com/questions/36932/whats-the-best-way-to-implement-an-enum-in-python
# This is bad because it only works at run time
# Also, enums have been rejected

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)
#
#if __name__ == "__main__":
#    post_departments(departments)
#    for s in schema_description.sections:
#        pass
#        pprint (s['name'])
#
#
#    metadata_sets()
    
#    data = canada_test_package.keys()
#    #print "---- Test Data Fields ---- " + str(len(test_data_fields))
#    print sorted(s.decode('utf8') for s in test_data_fields)
    #pprint(sorted(data.keys()))
    #pprint (sorted(schema_description.fields))
    
    #print "---- Schema Fields ---- " + str(len(set(schema_set)))
    #Sprint sorted(schema_set)


    #Sprint len(test_data_fields - schema_set)
    #Sprint sorted(test_data_fields - schema_set)    
#    difference1 = set(test_data_fields).difference(set(schema))
#    difference2 = set(schema).difference(set(test_data_fields))
#    print "Difference 1 " + str(len(difference1))
#    print sorted(difference1)
#    print "Difference 2 " + str(len(difference1))
#    print sorted(difference2)    
#    print "Common Elements"
#    pprint (sorted(set(test_data_fields) - (set(schema))))
#    print sorted(set(data).difference(set(schema)))

#    for section in schema_description.sections:
#        print section
##        for ckan_id, lang, f in schema_description.fields_by_ckan_id(include_existing=True):
##            print f
#        
        
   
   