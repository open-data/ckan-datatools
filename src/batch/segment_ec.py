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
langcodes={'D892EF88-739B-43DE-BDAF-B7AB01C35B30':'English',
           'FA6486B4-8A2A-4DA4-A727-E4EA3D29BF71':'French',
           '790CE47F-0B49-4D1F-9CE0-50EC57517981':'Bilingual'
           }

''' This could be lowercased to reduce number of hits, but then reporting would be less useful '''
language_markers=[
                   (' - English Version [AAFC-AIMIS-RP-', ' - French Version [AAFC-AIMIS-RP-'),
                    (' - English Version',' - French Version'),
                    (' - English version',' - French version'),
                    (' (in English)', ' (in French)'),
                    (' (In English)', ' (In French)'),
                    ('(- English)', '(- French)'),  
                    (' (English',' (French'),
                    (' (English',' (Fench'),
                    (' English',' French'),
                    (' - ENGLISH VERSION', ' - FRENCH VERSION')
                    
                    ]



def split_xml_files(pilot_file):

    cnt = Counter()
    tree = etree.parse(pilot_file)
    root = tree.getroot()
    special_title_numbers=[]
    split_en=[]
    split_fr=[]
    not_split=[]

    for i,child in enumerate(root):
        # TOTAL RECORDS
        cnt['TotalRecords']+=1
        #print i+1,child.tag
        if "CVReferenceCountByFormtype" in etree.tostring(child):
            cnt['CVReferenceCountByFormtype']+=1
            continue      
        formid = None           
        try: 
            # RECORDS WITH FORM ID
            formid = child.xpath("FORM[NAME='thisformid']/A")
            #print i,formid[0].text
            cnt['formids']+=1
            
            
            # GET THE TITLE
            title = child.xpath("FORM[NAME='title_en']/A/text()")[0]
            
            ''' Sadly there is no discernable pattern in this title element
            if "[AAFC-AIMIS-RP" in title: 
                cnt["[AAFC-AIMIS-RP-"]+=1
                num= title.split("[AAFC-AIMIS-RP-")[1].split("]")[0]
            '''

                
            # GET ALL RECORDS WITH language or language__ LANGUAGE INDICATORS
            # Document instances of records that do not have one.
            language=None
            langcode=None
            
            try:
                language__ = child.xpath("FORM[NAME='language__']/A") 
               
                if language__: 
                    cnt['language__']+=1
                else:
                    language = child.xpath("FORM[NAME='language']/A") 
                    if language: 
                       cnt['language']+=1
                       language__=language
                    


                langcode=language__[0].text
                if langcode: 
                    langcode = langcode.split('|')[1]
                else:
                    
                    cnt['no langcode']+=1
                    continue
            except:
                cnt["empty language Element"]
                raise
                
                #langcode=language[0].text
                continue
                 
            try:
                # NUMBER OF BILINGUAL RECORDS
                language = langcodes[langcode]
                cnt[language]+=1
                #print i,language, title
                '''Skip language matching for  Bilingual Records; TODO: write to separate file '''        
                if language == u'Bilingual':          
                    continue
                
                ''' collect titles that have a langauge, but no langauge marker '''
                split_marker=False
                split_title=None
                ''' Split the titles so they can be matched '''
                for marker in language_markers:
                    
                    if language=="English" and marker[0] in title:
                        split_title = title.split(marker[0])[0]
                        split_marker=True
                    elif language =="French" and marker[1] in title:
                        split_title = title.split(marker[1])[0]
                        split_marker=True
                        break
                   
         
                if split_marker == False:
                    print i,"NO SPLIT ::",language,"::",title
                    
                    cnt['NO SPLIT']+=1
                    if language=="English":
                        cnt['NO SPLIT English']
                    if language=="French":
                        cnt['NO SPLIT English']
                        
                elif language== "English":
                    #print i,"EN SPLIT", title
                    cnt['EN SPLIT']+=1
                elif language=="French":
                    #print i,"FR SPLIT", title
                    cnt['FR SPLIT']+=1
                    
                #if i>1000:sys.exit()
                    
                
                
            except:
               print "WOOOT"
               raise
            
        except:
            print "FAIL", formid
            raise
#            pprint(etree.tostring(child))

    pprint(cnt.items())  



def match_eng_fra():

    cnt = Counter()
    pilot_file =  "/Users/peder/dev/goc/OD_DatasetDump-0-partial.xml" 
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
            langcode=None
            
            #print i, "language__", language[0].text
            
            try:
                language = child.xpath("FORM[NAME='language']/A") 
                langcode=language[0].text
                cnt['language']+=1
                language = child.xpath("FORM[NAME='language__']/A") 
                langcode=language[0].text
                cnt['language__']+=1
            except:
                raise
                cnt['no langugage form elem']+=1
                #print formid[0].text

            try:
                langcode = langcode.split("|")[1]
            except:
                raise
                cnt['langcode blank in lanugage element']+=1
            
            try: 
                # NUMBER OF BILINGUAL RECORDS
               
                print langcode, language
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
    pilot_file =  "/Users/peder/dev/goc/OD_DatasetDump-0.xml" 
    split_xml_files(pilot_file)
    #match_eng_fra()
   