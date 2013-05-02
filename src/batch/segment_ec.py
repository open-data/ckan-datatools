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
language_markers=[
                    (' - English Version',' - French Version'),
                    (' (in English)', ' (in French)'),
                    (' (In English)', ' (In French)'),
                    ('(- English)', '(- French)'),  
                     (' (English version)',' (French version)'),
                    (' (English Version)',' (French Version)'),
                    [' [ ', ]
                    ]
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
    eng_records_no_marker=[]
    eng_records=[]
    
    fra_records={}
    
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
            title = child.xpath("FORM[NAME='title_en']/A/text()")[0]
            #print title
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
               
                
            try:
                langcode = langcode.split("|")[1]
                # NUMBER OF BILINGUAL RECORDS
                language = schema_description.dataset_field_by_id['language']['choices_by_pilot_uuid'][langcode]['key']

                cnt[language]+=1
                
                if language == u'English | Anglais':
                                    

                    cnt['English']+=1
                    short_title=None
                    for marker in language_markers:

                        if marker[0] in title:
                            short_title = title.split(marker[0])[0]
                            break

                    if short_title:
                        #print "---------------"
                        eng=(short_title,child)
                    else:
                       eng=(title,child)
                    #print "ENG", eng[0]
                    eng_records.append(eng)

                    
                elif language==u"French | Fran\u00e7ais":
                   
                    #print i,last_eng_title 
                    short_title=None
                    for marker in language_markers:
                        if marker[1] in title:
                            short_title_fr = title.split(marker[1])[0]
                            break
                  
                    if short_title_fr:
                       fra=(short_title_fr, child)
                    else:
                       fra=(title,child)
                    #print "FRA", fra[0]
                    fra_records[fra[0]]=fra[1]

                # now we can match the two arrays
                
            except:
                
                #raise
                '''
                for node_en in eng_records:
                print "WE HAVE ONE"
                
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
        '''         
        except:
            #print "BLAH ", formid
            raise

    
#    pprint(fra_records.keys())
#    print len(fra_records.items())
    unmatched=[]
    print "<XML>\n"
    for i, en in enumerate(eng_records):
        
        en_title=en[0]
        # Now find this in french 
        try:
            node_en = etree.tostring(en[1])
            node_fr = etree.tostring(fra_records[en_title])
            
#            print "EEEEEEEEENNNG", i, en_title
#            print "FRAAAAAAAAAAA" , i,fra_records[en_title]
            print node_en
            print node_fr
            #sys.exit()
        except KeyError:
            #raise
            #print "Cannot match ", en_title
            unmatched.append(en)
        except:
            raise
        
        
    print "\n</XML>"
          
        
        
        
        
    #pprint(cnt.items())
    

if __name__ == "__main__":
    match_eng_fra()
   