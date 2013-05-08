import sys
from datetime import date
from lxml import etree
from pprint import pprint
from collections import Counter
import common
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

def split_xml_files(pilot_file):

    cnt = Counter()
    dept_cnt = Counter()
    tree = etree.parse(pilot_file)
    root = tree.getroot()
    special_title_numbers=[]
    docs_en=[]
    fra_dict={}
    docs_unsplit_titles=[]
    docs_bilingual=[]
    matched=[]
    unmatched=[]


    for i,child in enumerate(root):
        # TOTAL RECORDS
        

        #print i+1,child.tag
        if "CVReferenceCountByFormtype" in etree.tostring(child):
            cnt['CVReferenceCountByFormtype']+=1
            continue  
        else:
            cnt['TotalRecords']+=1
        # Throw out any records that are incomplete
        # Count number of FORM elements   
  
        cnt[len(child.xpath("FORM"))]+=1
       
       
        formid = None           
        try: 
            # RECORDS WITH FORM ID
            formid = child.xpath("FORM[NAME='thisformid']/A/text()")[0]
            if len(child.xpath("FORM[NAME='number_datasets']/A/text()")) ==0:
                pass
                #print "ZERO ? or ...", child.xpath("FORM[NAME='dataset_link_en_1']/A/text()")
            
            #print i,formid[0].text
            cnt['formid']+=1
        except IndexError:
            cnt['no formid']+=1   
            continue
        try:
            # GET THE TITLE
            title = child.xpath("FORM[NAME='title_en']/A/text()")[0]
            #keywords  =child.xpath("FORM[NAME='title_fr']/A/text()")[0]
           
              
                
            ''' Sadly there is no discernable pattern in this title element
            if "[AAFC-AIMIS-RP" in title: 
                cnt["[AAFC-AIMIS-RP-"]+=1
                num= title.split("[AAFC-AIMIS-RP-")[1].split("]")[0]
            '''

                
            # GET ALL RECORDS WITH language or language__ LANGUAGE INDICATORS
            # Document instances of records that do not have one.
            language=None
            langcode=None
            'count departments'
            try:

                dept_code=child.xpath("FORM[NAME='department']/A/text()")[0].split('|')[1]
                print dept_code
                dept= schema_description.dataset_field_by_id['owner_org']['choices_by_pilot_uuid'][dept_code]['eng']
                dept_cnt[dept]+=1
                dept_cnt["TOTAL DEPARTMENTAL RECORDS"]+=1
            except:
                dept_cnt['No Department']+=1
                raise
#            try:
#                dict_en = child.xpath("FORM[NAME='dictionary_list:_en']/A")
#                dict_fr = child.xpath("FORM[NAME='data_dictionary_fr']/A")
#                
#                if dict_en[0].text:
#                    print dict_en[0].text.lstrip()
#                    dept= child.xpath("FORM[NAME='department']/A")[0].text
#                    cnt["Dictionary List:EN"]+=1
#                    cnt[dept]+=1
#                if dict_fr[0].text:
#                    print dict_fr[0].text.lstrip()
#                    dept= child.xpath("FORM[NAME='department']/A")[0].text
#                    cnt["Dictionary List:FR"]+=1
#                    cnt[dept]+=1
#
#            except:
#                pass
#                #print "NO SCRIPT TAG"

            try:
                language__ = child.xpath("FORM[NAME='language__']/A") 
               
                if language__: 
                    cnt['language__']+=1
                elif language__ == []:
                    cnt['no language code']
                    continue
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
            except Exception as e:
                print e
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
#                if language == u'Bilingual': 
#                    print "-----------"
#                    print formid, language
#                    print child.xpath("FORM[NAME='dataset_link_en_1']/A/text()")
#                    print child.xpath("FORM[NAME='dataset_link_fr_1']/A/text()")
#                    print "-----------"
#                    #docs_bilingual.append(child)         
#                continue
                
                
                ''' collect titles that have a langauge, but no langauge marker '''
                split_marker=False
                split_title=None
                ''' Split the titles so they can be matched '''
                for marker in common.language_markers:
                    
                    
                    if language=="English" and marker[0] in title:
                        split_title = title.split(marker[0])[0]
                        split_marker=True
                    elif language =="French" and marker[1] in title:
                        split_title = title.split(marker[1])[0]
                        split_marker=True
                        break
                   
         
                if split_marker == False:
                    #print i,"NO SPLIT ::",language,"::",title
                    
                    cnt['NO SPLIT']+=1

                elif language== "English" and "French" not in title:
                    #print i,"EN SPLIT", title
                    docs_en.append((split_title,child))
                    cnt['EN SPLIT']+=1
                elif language=="French" and "English" not in title:
                    #print i,"FR SPLIT", title
                    fra_dict[split_title] =child
                    cnt['FR SPLIT']+=1

            except Exception as e:
               print  e
               raise
            
        except Exception as e:
            print e
            print "FAIL",i, formid
            raise
#            pprint(etree.tostring(child))


    #print len(docs_en),len(fra_dict),len(docs_unsplit_titles),len(docs_bilingual)
    ''' with these lists ready, we can now do some matchin work '''

    #print "SIZE OF FRA DICT ", len(fra_dict)
    foo=False
    ''' Let's match records '''
    for i, en in enumerate(docs_en):
       
        en_title=en[0]
           
        # Now find this in french 
        try:   
             check = fra_dict[en_title]# match first before appending english record so both fail and ENG / FRA sequence does not get broken       
             matched.append(en[1])
             matched.append(fra_dict[en_title])
             cnt["matched"]+=1
        except KeyError:
            
            unmatched.append(en)
            cnt["unmatched"]+=1
        except:
            raise      

    #print "========== MATCH: {} == NO MATCH: {} ===========".format(len(matched),len(unmatched))
    
    '''  Now we can build the new XML document '''
#    root = etree.Element("XML")
#    print "<XML>"
#    for record in matched:
#        #if foo:
#        print etree.tostring(record), "\n"
#            #foo = False
#        
#    print "</XML>"
        #root.append(record)
#        if foo:
#      
#            print etree.tostring(root)
#            sys.exit()
#            

    #outfile =  "/Users/peder/dev/goc/pilot-matched-{}.xml".format((date.today()))
    
    #with open(outfile,'w') as f:
      #f.write(etree.tostring(root))

    #pprint(cnt.items())
    
    for item in dept_cnt.items().sort():
        print item[0], item[1]
    print "Total Number of Departments ", len(dept_cnt)-1

    print "Bilingual Records", cnt["Bilingual"]
    print "Matched Records", cnt["matched"]*2
    print "Total Processed", cnt["Bilingual"]+(cnt["matched"]*2)
    
    print "Total Records", (cnt["TotalRecords"]-  # Total number of <RECORD> Elements in the file
                           cnt['CVReferenceCountByFormtype']-  #5 of these are irrelevant
                           cnt['no langcode']-    # Some don't have any language code
                           cnt['no formid']-   # Some are missing the formid (UUID), so they should be exluded
                           cnt['NO SPLIT']   #
                           )
    
 
if __name__ == "__main__":
    #pilot_file =  "/Users/peder/dev/goc/OD_DatasetDump-0.xml" 
    pilot_file="/Users/peder/dev/goc/PublishedOpendata-0.xml"
    #pilot_file="/Users/peder/dev/goc/PendingOpendata-0.xml"
    split_xml_files(pilot_file)

   