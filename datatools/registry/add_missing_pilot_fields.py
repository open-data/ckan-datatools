import sys
from lxml import etree
import ckanapi
import helpers
import resource
from pprint import pprint
from datatools.batch.common import language
from ckanext.canada.metadata_schema import schema_description


'''
    For every pilot data field that was entered into registry, category_type and subject is missing.
    
    Procedure for fixing this:
    
    1. For every id grab these values from Pilot XML and create list of tuples:
    [(id, subjec, category_type),...
    2. For every tuple:
        i. Get package in registry
        ii.Check to see if the two fields are empty, if so, update them
        iii. Write the package back.
        
    
'''


if __name__ == "__main__":
    pilot_xml = '/Users/peder/dev/OpenData/data_sources/pilot/final.xml'
    tree = etree.parse(pilot_xml)
    root = tree.getroot()
    ''' NOTE - Searching the XML Tree directly is very slow: eg
    print root.xpath('//FORMID[text()="%s"]/../CATEGORY/text()'% id)[0].split('|')[-1]
    '''
    subject_types=schema_description.dataset_field_by_id['subject']['choices_by_pilot_uuid']
    print subject_types
    subjects={}

    for child in root:
       try:
          
           formid = child.xpath("FORM[NAME='thisformid']/A/text()")[0]
           # WARNING CKAN SUBJECT = Category in Pilot
           sub = child.xpath("FORM[NAME='category']/A/text()")[0]
           subject = sub.split('|')[-1]
           subjects[formid]= subject_types[subject]['key']
           
       except:
           
           print "bad record"
    
    # Now with a list of subjects we can check to see if the ID is on the registry, 
    # and then update the field 
    registry = ckanapi.RemoteCKAN('http://localhost:5000', apikey='tester')
    '''
    1.  Get the package 
    2. Change the package
    3. Update the package
    '''
    print "---------------------"
    for id,subject in subjects.iteritems():
        print id.lower()
        pack = registry.action.package_show(name_or_id=id.lower())
        print pack['subject']
        if not pack['subject']: pack['subject'] = [subject]
       
        result = registry.action.package_update(**pack)
        pack = registry.action.package_show(name_or_id=id.lower())
        print pack['subject']
                        