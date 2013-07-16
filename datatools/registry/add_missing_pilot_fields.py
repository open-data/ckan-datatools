#-*- coding:UTF-8 -*-
import sys
from lxml import etree
import ckanapi
import helpers
#import resource
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
    pilot_xml = '/Users/jakoped/Documents/OpenData/final.xml'
    tree = etree.parse(pilot_xml)
    root = tree.getroot()
    ''' NOTE - Searching the XML Tree directly is very slow: eg
    print root.xpath('//FORMID[text()="%s"]/../CATEGORY/text()'% id)[0].split('|')[-1]
    '''
    subject_types=schema_description.dataset_field_by_id['subject']['choices_by_pilot_uuid']
    print subject_types
    subjects={}
    resume_flag=False
    for child in root:
       try:
           
           formid = child.xpath("FORM[NAME='thisformid']/A/text()")[0]
           if formid.lower()=='f80bbec0-0a48-4fe6-8efd-fa1b7bfbe6cb': resume_flag=True
           # WARNING CKAN SUBJECT = Category in Pilot
           sub = child.xpath("FORM[NAME='category']/A/text()")[0]
           subject = sub.split('|')[-1]
           if resume_flag:
               subjects[formid]= subject_types[subject]['key']
           else:
               print "Skip", formid.lower()
           
       except:
           
           print "bad record"
    
    # Now with a list of subjects we can check to see if the ID is on the registry, 
    # and then update the field 
    registry = ckanapi.RemoteCKAN('http://registry.statcan.gc.ca',apikey='4c57004e-fe2a-496d-8bef-8dbe98ba91e4')
   
    '''
    1.  Get the package 
    2. Change the package
    3. Update the package
    '''
    
    print "---------- Updating -----------", len(subjects)
    n=0
    for id,subject in subjects.iteritems():
        n+=1
        try:
            pack = registry.action.package_show(name_or_id=id.lower())
            print n, id.lower(), ",",  pack['subject'], pack['catalog_type']
            pack['catalog_type']=""
            if not pack['subject'] or not pack['catalog_type']: 
                print "yeahh"
                sys.exit()
                pack['subject'] = [subject]
                pack['catalog_type'] = u"Data | Données"
                result = registry.action.package_update(**pack)
                pack = registry.action.package_show(name_or_id=id.lower())
              
                print n, id.lower(), ", Updating", id, pack['subject'], pack['catalog_type']
        except:
               
                print n, id.lower(), ", No Record"
                pass
            #print ("No record:  http://registry.statcan.gc.ca/en/dataset/%s" % id.lower())

                        