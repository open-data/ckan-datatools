import sys
from lxml import etree
from pprint import pprint
from collections import Counter
from ckanext.canada.metadata_schema import schema_description

"""
    1. Load pilot file into memory, check size and number of RECORDS
    2. Remove any RECORDS that are missing the FORM, check number and size
    3. Segment all bilingual records, double check that there are no matching titles
    6. Check number of records that have dicionary_list_en
    8. Use "other" for formats that are not in the schema list 
    9. Fiddle with chain of responsibility pattern
    
    168 Records have  language instead of language__
    There are 1445 bilingual records.  Only 1098 made it into the bilingual .jl file due to date errors or other issues.
      
"""

def split_xml_files():
    cnt = Counter()
    print "Report"
    pilot_file =  "/Users/peder/dev/goc/OD_DatasetDump-0.xml" 
    tree = etree.parse(pilot_file)
    
    root = tree.getroot()
    print (sys.getsizeof(root))

    for i,child in enumerate(root):
        # TOTAL RECORDS
        cnt['TotalRecords']+=1
        #print i+1,child.tag
        if "CVReferenceCountByFormtype" in etree.tostring(child):
            cnt['CVReferenceCountByFormtype']+=1
            continue       
        
        try: 
            # RECORDS WITH FORM ID
            formid = child.xpath("FORM[NAME='thisformid']/A")
            #print i,formid[0].text
            cnt['formids']+=1
            
            
            # RECORDS WITH LANGUAGE INDICATOR
            langcode=''
            language__ = child.xpath("FORM[NAME='language__']/A") 
            #print i, "language__", language[0].text
            
            try:
                langcode=language__[0].text
                cnt['language__']+=1
            except:
                cnt['no langugage__ form elem']+=1
                #print formid[0].text
                language = child.xpath("FORM[NAME='language']/A") 
                langcode=language[0].text
                #print i, "language", language[0].text
                cnt['language']+=1
            try:
                langcode = langcode.split("|")[1]
                # NUMBER OF BILINGUAL RECORDS
                language = schema_description.dataset_field_by_id['language']['choices_by_pilot_uuid'][langcode]['key']
                #print language
                cnt[language]+=1
                if language != u'Bilingual (English and French) | Bilingue (Anglais et Fran\xe7ais)':
                    print etree.tostring(child)
                
            except:
                cnt['language element without language']+=1
                # FALL BACK TO <DC.LANGUAGE>En</DC.LANGUAGE>
            
        except:
            pprint(etree.tostring(child))

    pprint(cnt.items())   


def match_eng_fra():
    print "Matching English and French"
    cnt = Counter()
    pilot_file =  "/Users/peder/dev/goc/OD_DatasetDump-0.xml" 
    tree = etree.parse(pilot_file)
    root = tree.getroot()
    # Find the first English file
    eng=False
    fra=True
    last_node=''
    last_language=''
    last_name=''
    last_eng_title=""
    total_matched=0
    for i,child in enumerate(root):
        # TOTAL RECORDS
        cnt['TotalRecords']+=1
        #print i+1,child.tag
        if "CVReferenceCountByFormtype" in etree.tostring(child):
            cnt['CVReferenceCountByFormtype']+=1
            continue
        
        
        try: 
            # RECORDS WITH FORM ID
            formid = child.xpath("FORM[NAME='thisformid']/A")
            #print i,formid[0].text
            cnt['formids']+=1
            
            
            
            # RECORDS WITH LANGUAGE INDICATOR
            langcode=''
            language__ = child.xpath("FORM[NAME='language__']/A") 
            #print i, "language__", language[0].text
            
            try:
                langcode=language__[0].text
                cnt['language__']+=1
            except:
                cnt['no langugage__ form elem']+=1
                #print formid[0].text
                language = child.xpath("FORM[NAME='language']/A") 
                langcode=language[0].text
                #print i, "language", language[0].text
                cnt['language']+=1
            try:
                langcode = langcode.split("|")[1]
                # NUMBER OF BILINGUAL RECORDS
                language = schema_description.dataset_field_by_id['language']['choices_by_pilot_uuid'][langcode]['key']
                #print language
                cnt[language]+=1
                if language == u'English | Anglais':
                    last_language=language
                    last_node = child
                    cnt['English']+=1
                    last_eng_title = child.xpath("FORM[NAME='title_en']/A/text()")[0]
                    
                if language==u"French | Fran\u00e7ais" and last_language =='English | Anglais':
                    #print i,last_eng_title 
                    title= child.xpath("FORM[NAME='title_en']/A/text()")[0]
#                    print last_eng_title.split(" ")[1:4]
#                    print title.split(" ")[1:4]
                    if last_eng_title.split(" ")[1:4] == title.split(" ")[1:4]:
                       
                        total_matched+=1
                        cnt["GOOD MATCH"]+=1
                        print etree.tostring(last_node)
                        print etree.tostring(child)
                    else: 
                        cnt["POOR MATCH"]+=1
                       
                    #print i, title
                   
                    # CHECK TITLE QUIVALENCY
                    cnt["ENG_FRA-SEQUENCED-Maybe"]
                    cnt['French']+=1
                    #print etree.tostring(child)
            except:
                #raise
                print "LANG ERROR"
                    
        except:
            print formid
            raise
    print "TOTAL MATCHED ", total_matched
    pprint(cnt.items())

if __name__ == "__main__":
    match_eng_fra()
   