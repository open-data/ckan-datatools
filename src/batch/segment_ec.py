# coding=utf-8
import sys
import csv
from datetime import date
from lxml import etree
from pprint import pprint
from collections import Counter
import common
import pickle
from ckanext.canada.metadata_schema import schema_description
from prettytable import PrettyTable, from_csv





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
cnt = Counter()
dept_cnt = Counter()
tree = None
root =None
special_title_numbers=[]
docs_en=[]
fra_dict={}
docs_unsplit_titles=[]
docs_bilingual=[]
matched=[]
unmatched=[]
agri_cnt=Counter()
pending_departments = pickle.load(open('pending_departments.pkl','rb'))



def meat_fix(title):
    
    return title.replace("Lamb, Bison, Beef, Goat, Mutton, Pork, Veal, Horsemeat","Beef, Bison, Goat, Horsemeat, Lamb, Mutton, Pork, Veal").replace('Turkey, Chicken, Mature Chicken','Chicken, Mature Chicken, Turkey')


def matched_ids():
    fp = open('wayward.csv', 'r')
    with open('wayward.csv', 'rb') as csvfile:
        return [(row[0].upper(),row[1].strip()) for row in csv.reader(csvfile, delimiter=',')]


def split_xml_files(pilot_file):

    tree = etree.parse(pilot_file)
    root = tree.getroot()
    
    
    for i,child in enumerate(root):
        
        # Ignore these 5 records, they are for configuration
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
            title=None
            title_elem = child.xpath("FORM[NAME='title_en']/A/text()")
            if title_elem: 
                title = meat_fix(title_elem[0])
                
            else:
                cnt["Title Element Missing"]
  
            ''' Sadly there is no discernable pattern in this title element
            if "[AAFC-AIMIS-RP" in title: 
                cnt["[AAFC-AIMIS-RP-"]+=1
                num= title.split("[AAFC-AIMIS-RP-")[1].split("]")[0]
            '''

                
            # GET ALL RECORDS WITH language or language__ LANGUAGE INDICATORS
            # Document instances of records that do not have one.
            language=None
            langcode=None
            '''count departments'''
            try:

                dept_code=child.xpath("FORM[NAME='department']/A/text()")[0].split('|')[1]
                #print dept_code
                dept= schema_description.dataset_field_by_id['owner_org']['choices_by_pilot_uuid'][dept_code]['eng']
                dept_cnt[dept]+=1

                cnt["Total Records with Department"]+=1
            except:
                cnt['No Department Found']+=1
       

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

                
                ''' collect titles that have a langauge, but no langauge marker '''
                split_marker=False
                split_title=None
                ''' Split the titles so they can be matched '''
                for marker in common.language_markers:
                                 
                    if language=="English" and marker[0] in title:
                        split_title = title.split(marker[0])[0]
                        split_marker=True
                        break
                    elif language =="French" and marker[1] in title:
                        split_title = title.split(marker[1])[0]
                        split_marker=True
                        break
                   
         
                if split_marker == False:
                    #print i,"NO SPLIT ::",language,"::",title
                    
                    cnt['NO SPLIT']+=1

                elif language== "English" and "French" not in title:
                    #print i,"EN SPLIT", title
                    docs_en.append((split_title,child,formid))
                    cnt['EN SPLIT']+=1
                elif language=="French" and "English" not in title:
                    #print i,"FR SPLIT", title
                    fra_dict[split_title] =child
                    cnt['FR SPLIT']+=1
                else:
                    unmatched.append((title,child, formid))
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
        
        
    print len(matched)
    manually_matched=matched_ids()
    for m in manually_matched:
        print "Searching for ", m
        e = "//FORM[NAME='thisformid'][A/text()='{}']".format(m[0])
        matched.append(root.xpath(e)[0].getparent())
        f = "//FORM[NAME='thisformid'][A/text()='{}']".format(m[1])        
        matched.append(root.xpath(f)[0].getparent())   
            
    print len(matched)
   
    
    def write_xml():

        print "========== MATCH: {} == NO MATCH: {} ===========".format(len(matched),len(unmatched))
        
        '''  Now we can build the new XML document '''
        root = etree.Element("XML")

        for i, record in enumerate(matched):
            #print i, record
            root.append(record)
#            if foo:
#          
#                print etree.tostring(root)
#                sys.exit()
            

        outfile =  "/Users/peder/dev/goc/LOAD/pilot-matched.xml"
    
        with open(outfile,'w') as f:
            f.write(etree.tostring(root))
    
    write_xml()  
       
  
    def report():
        f = open('unmatched.csv', 'wt')
        
        writer = csv.writer(f)
        writer.writerow(['No.','Department','ID','Name','Language'])
        
       
        for i,item in enumerate(unmatched):
            #print item[0]
            child = item[1]
            formid = child.xpath("FORM[NAME='thisformid']/A/text()")[0]
            title = item[0]
            try:
                dept_code=child.xpath("FORM[NAME='department']/A/text()")[0].split('|')[1]
                department= schema_description.dataset_field_by_id['owner_org']['choices_by_pilot_uuid'][dept_code]['eng']
            except:
                department = None
            language = "English"
            writer.writerow([i,department, formid.lower(), title, language])
            
    report()   
    def dept_tables():
        #pickle.dump(dept_cnt, open('pending_departments.pkl','wb'))
        
        #pending_departments = pickle.load(open('pending_departments.pkl','rb'))
                
        print "Pending", sum(pending_departments.values())
        print "Published", sum(dept_cnt.values())
        #print set(pending_departments.items())
        #print list(set(pending_departments.items()) & set(dept_cnt.items()))
        #print [d for d in pending_departments.items()]
        
        # create a list of tuples 
        #[(key, value)]
        
        published_column = []
        for department in pending_departments:
            print ">>",department
            if dept_cnt.has_key(department):
                published_column.append(dept_cnt[department])
            else:
                published_column.append(0)
        
        print published_column 
        
        
            
        print pending_departments
        f = open('departments.csv', 'wt')
        
        writer = csv.writer(f)
       
        x=PrettyTable()
        dept_column = [item[0] for item in pending_departments.items()]
        x.add_column("Department Name", pending_departments.keys(), 'l', 't')
        x.add_column("Published",published_column,'r')
        x.add_column("Pending",pending_departments.values(),'r')
        print x  
  
        writer.writerow(['Department Name','Pending XML','Online'])
        ''' Create table to add data to  '''
       
        #print u'\u2019'.encode('utf-8') .replace(u'\u2019','') #Fix bad windows chars
        for department, count in sorted(pending_departments.items()):
            writer.writerow([department,
                     count,
                     '',
                     ])         
        
        f.close()    
        print writer
        
        fp = open('departments.csv', 'r')
        
        pt = from_csv(fp)
        pt.align['Department Name'] = "l" # Left align city names
        pt.padding_width = 1 # One space between column edges and contents (default)
        print pt
        '''
        print "Department Counts"
        print "-----------------"
        print "Total Number of Departments ", len(dept_cnt)
        print "\n"
        for department, count in sorted(dept_cnt.items()):
            print count
        
        print 
        print "Raw Report"
        print "----------"
        for i,n in cnt.items():
            print i,n
        print "\n"    
        print "Summary"
        print "-------"
        
    
        print "Bilingual Records", cnt["Bilingual"]
        print "Matched Records", cnt["matched"]*2
        print "Total Processed", cnt["Bilingual"]+(cnt["matched"]*2)
        
        print "Total Records", (cnt["TotalRecords"]-  # Total number of <RECORD> Elements in the file
                               cnt['CVReferenceCountByFormtype']-  #5 of these are irrelevant
                               cnt['no langcode']-    # Some don't have any language code
                               cnt['no formid']-   # Some are missing the formid (UUID), so they should be exluded
                               cnt['NO SPLIT']   #
                               )
    '''
    #report()
    
    
    def load_report_data():
        pass

if __name__ == "__main__":

    #pilot_file =  "/Users/peder/dev/goc/OD_DatasetDump-0-partial.xml" 
    pilot_file="/Users/peder/dev/goc/PublishedOpendata-0.xml"
    #pilot_file="/Users/peder/dev/goc/PendingOpendata-0.xml"
    split_xml_files(pilot_file)

   