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

skip=['062480AF-2E32-4F89-8D61-55160B8E3625',
      '99D6FF56-30D6-478B-AF74-9A0348CDDDDB',]

missing_in_new=[u'dafb6413-5dab-45ca-bcd2-8c6ff4b67be5',
 u'a15918d9-fcf7-4e62-a983-e5965400abd0',
 u'26ca2ddc-6aaf-4d96-9dc0-26757f9c8a0d',
 u'9e4f8e40-e390-46ee-8f34-a2719ca65f67',
 u'7606bc7b-c032-4b57-8706-02ecb71ac7d0',
 u'dab5596d-dcd3-48e3-8594-b129dc68d5c6',
 u'8c8dbf45-e706-4120-be22-4aef7635fce5',
 u'7d226eef-b7bc-4f44-8828-13b70e33dd1d',
 u'be106be3-5ee0-42f1-8e56-f38a21c5297e',
 u'8b5d3d07-e00c-4b69-9046-8a2de8450777',
 u'145a12e9-83f9-4c81-a68a-c213e9a3c05e',
 u'249688da-769c-49dc-b0b9-449b8e0666db',
 u'6c19a1c5-a173-463b-a7bd-817c2d35802c',
 u'bbef9e90-e622-44c7-aa90-a635f5e422a0',
 u'6bac7d85-195c-4c82-9076-9d3cd00dafee',
 u'30582c5a-f9d7-4932-ada1-dae4ea4a58e2',
 u'17c6703f-be6a-42cc-9817-e9779eeba352',
 u'9a0208f1-dbad-4700-af24-fc8886206b96',
 u'aa73f174-1fab-4ac7-bc19-79d972044b05',
 u'b4670f58-8bed-44f5-b41a-b96516cefb8f',
 u'c20c8d52-4a05-43e0-8075-609cb8dcd85c',
 u'653e3ade-56a2-489c-97c9-1f7d930cedba',
 u'0f1f9599-5057-40d5-b003-8761e85bccc1',
 u'dfb9b20e-c014-4601-9a3b-19a688b203a9',
 u'602dd153-b61c-46dc-91b2-89cd5b8f8e45',
 u'53390d03-5a71-40e9-8fa9-4d0572b4cf45',
 u'97215cfe-504a-4bde-b211-d194751e742a',
 u'b8df23da-1925-4a9a-99bc-3f99da83b2c2',
 u'8bf5752a-fd2b-4999-bb65-1182d6f20f2a',
 u'6e7fb3cf-c3e8-491b-9628-461c2f5aa0be',
 u'd5024e6d-f261-4acb-abdb-636a9cae5de4',
 u'a941f632-8d41-44e5-b34b-b48fe26b1db6',
 u'5a891037-1c83-4483-9137-5e980c8a23b6',
 u'adfa15c1-7238-4967-be00-1524bbf66b60',
 u'ee82dff4-8668-470b-8c7d-0de51b338994',
 u'3f66f90d-90f8-4aec-b369-e744073788ae',
 u'4d75cf10-92a4-4cb5-8838-a5b745c18359',
 u'15f677ee-eb80-40f7-b323-c530dae84f18',
 u'72d5dd81-1c4c-4d31-ad56-8522c6f161aa',
 u'48c2bc61-72c8-401a-a8f7-207710f7b0cc',
 u'76f4fbaf-5daf-4006-b3fe-915fae43d589',
 u'fbd347fe-acb5-4930-95b8-7daf5940e519',
 u'b3e6feb8-43cd-4a05-8c10-458639d96e51',
 u'8cb47266-ce22-43eb-81c3-13c6d0f46d6b',
 u'd4d5fd46-64e8-4acd-b95c-69bfcd99fef6',
 u'1b404660-a745-4e40-8bf9-7c0df298fc67',
 u'e1a3bc45-5bae-4bd9-806e-840841c0ba32',
 u'369865c9-949c-4647-b1f2-822339ba0890',
 u'47d7de89-e60d-4e2c-a8da-5d6ba70625af',
 u'ee84c92e-f1e3-4ca1-908b-b9c600bc866f',
 u'dd84f712-953a-4455-85e9-422c540d33b1',
 u'86b4e601-8c66-4baa-9257-205e5a864239',
 u'c38247aa-d704-4a2b-bd31-fe8bc7600744',
 u'fb89b81f-d64f-4e9b-9464-f1edeb35020e',
 u'64b450ef-7e30-453f-b245-fbab235d48cf',
 u'06201991-4f6e-4404-b417-ae83b94e7dc7',
 u'02071857-fbc4-42e8-adeb-0d0f9b3b562d',
 u'99d27654-c3f2-48f5-a053-7c772ae6563c',
 u'632cef40-9de6-47e5-9d16-744d32fc4f0e']




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

no_langauge_elem=[]

def meat_fix(title):
    
    return title.replace("Lamb, Bison, Beef, Goat, Mutton, Pork, Veal, Horsemeat","Beef, Bison, Goat, Horsemeat, Lamb, Mutton, Pork, Veal").replace('Turkey, Chicken, Mature Chicken','Chicken, Mature Chicken, Turkey')

def force_matched_pairs():
    with open('wayward.csv', 'r') as csvfile:
        return [(row[0].upper(),row[1].upper()) for row in csv.reader(csvfile, delimiter=',')]

def force_matched_ids():
    ids=[]
    for pair in force_matched_pairs():
        ids.append(pair[0])
        ids.append(pair[1])
    return ids
        

def find_pending(pilot_file):

    tree = etree.parse(pilot_file)
    root = tree.getroot()
       
    status_cnt = Counter()
    pending_records=[]
    for i,child in enumerate(root):
        
        # Ignore these 5 records, they are for configuration
        if "CVReferenceCountByFormtype" in etree.tostring(child):
            cnt['CVReferenceCountByFormtype']+=1
            continue  
        
        formid = None           
        try: 
            # RECORDS WITH FORM ID
            
            #formid = child.xpath("FORM[NAME='thisformid']/A/text()")[0]
            '''
                    <STATUS>Complete</STATUS>
                    <ADMINSTATUS>published</ADMINSTATUS>
                    <EDITIONSTATUS>draft</EDITIONSTATUS>
                    <FLOWSTATUS>published</FLOWSTATUS>
                                
            
            '''
   
            status = child.find("STATUS")
            adminstatus = child.find("ADMINSTATUS")
            editionstatus = child.find("EDITIONSTATUS")
            flowstatus = child.find("FLOWSTATUS")
            #if flowstatus.text != 'published': 
           
            if flowstatus.text == 'pending':  
                #print etree.tostring(child)  

                dept_code=child.find("DEPARTMENT").text.split("|")[1]
                dept= schema_description.dataset_field_by_id['owner_org']['choices_by_pilot_uuid'][dept_code]['eng']
             
                pending_records.append((
                            i,
                            dept,  
                            child.find("FORMID").text,
                            child.find("DC.TITLE").text,
                            child.find("FLOWSTATUS").text   
                            ),)
            
            '''
            try:
                status_cnt[status.text]+=1
                status_cnt[adminstatus.text]+=1
                status_cnt[editionstatus.text]+=1
                status_cnt[flowstatus.text]+=1
                if status.text=='pending':
                    print child.find("DEPARTMENT").text.split("|")[1]
                    pending_records.append[(
                         i,                 
                         child.find("DEPARTMENT").text.split("|")[1],
                         child.find("DC.TITLE").text,
                         child.find("FORMID").text,                 
                                           
                                           )]
                    
            except:
                pass
                #status_cnt['missing_value']+=1
 
            ''' 
        except:
            
            raise
#    pprint(pending_records)
#    print len(pending_records)
#    #pprint(status_cnt.items())


def split_xml_files(pilot_file):

    tree = etree.parse(pilot_file)
    root = tree.getroot()
    force_biling=[]
   
    with open('force-bilingual.csv', 'rb') as csvfile:
        for row in csv.reader(csvfile):
            force_biling.append(row[0].upper())
    
    
    matched_ids_en=[i[0] for i in force_matched_pairs()]
    matched_ids_fr=[i[1] for i in force_matched_pairs()]

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
            formid = child.xpath("FORM[NAME='thisformid']/A/text()")[0]
            if formid in missing_in_new:
                print "STOP Search process"
            if formid in skip:
                print "SKIPPING ", formid
                continue
            
            if formid.lower() in missing_in_new: 
                print "STOP ", formid.lower()
            if formid in force_matched_ids():
                continue
            if len(child.xpath("FORM[NAME='number_datasets']/A/text()")) ==0:
                cnt['number_datasets_zero']+=1

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
                if "Road Network File - 2011 - Canada" in title:
                    print "STOP", title
            else:
                cnt["Title Element Missing"]
  
            ''' Sadly there is no discernable pattern in this title element
            if "[AAFC-AIMIS-RP" in title: 
                cnt["[AAFC-AIMIS-RP-"]+=1
                num= title.split("[AAFC-AIMIS-RP-")[1].split("]")[0]
            '''

            # GET ALL RECORDS WITH language or language__ LANGUAGE INDICATORS
            # Document instances of records that do not have one.

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
                
                language = common.language(child)
                cnt[language]+=1
                if language=="Bilingual" or formid in force_biling:
                    docs_bilingual.append(child)
                    continue
            except:
                cnt["empty language Element"]
                no_langauge_elem.append(child)
                raise
                continue
   
            try:
                
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

                if language== "English":
                    #print i,"EN SPLIT", title
                    docs_en.append((split_title,child,formid))
                    cnt['EN SPLIT']+=1
                elif language=="French":
                    #print i,"FR SPLIT", title
                    fra_dict[split_title] =child
                    cnt['FR SPLIT']+=1
                else:
                    pass
                    
            except Exception as e:
               print  e
               raise
            
        except Exception as e:
            print e
            print "FAIL",i, formid
            raise
#            pprint(etree.tostring(child))


    #print len(docs_en),len(fra_dict),len(docs_unsplit_titles),len(docs_bilingual)
    ''' with these lists ready,  do some matching work '''

    for i, en in enumerate(docs_en):

        formid= en[1].xpath("FORM[NAME='thisformid']/A/text()")[0] 
        print "Trying to match ", formid
        if formid in missing_in_new:
            print "STOP Matching process"
        if formid.upper() in force_matched_ids():
            print "----------- FORCE MATCHED FOUND, SKIPPING ---------"
            continue
        
        # Now find this in french 
        try:  
             en_title=en[0]
             check = fra_dict[en_title]# match first before appending english record so both fail and ENG / FRA sequence does not get broken       
             print en_title
             print fra_dict[en_title].xpath("FORM[NAME='title_en']/A/text()")
             matched.append(en[1])
             matched.append(fra_dict[en_title])
             cnt["matched"]+=1
        except KeyError:
            raise
           
        except:
            raise 
        
 
    print "Matched before", len(matched)

    
    for m in force_matched_pairs():
        print "Searching for ", m
        e = "//FORM[NAME='thisformid'][A/text()='{}']".format(m[0])
        matched.append(root.xpath(e)[0].getparent())
        f = "//FORM[NAME='thisformid'][A/text()='{}']".format(m[1])     
        try:   
            matched.append(root.xpath(f)[0].getparent())
        except:
            print "FORM ID MISSING?", f  
        for un in unmatched:
            if m[0] == un[2]:
                unmatched.remove(un)
            if m[0] in force_biling:
                unmatched.remove(un)
            
    print "Matched after", len(matched)

    
    def write_xml():
        print "BILINGUAL ", len(docs_bilingual)
        print "MATCH: {} - NO MATCH: {} ".format(len(matched),len(unmatched))
        
        '''  Build the new XML document '''
        unmatched_root = etree.Element("XML")
        matched_root = etree.Element("XML")
        bilingual_root = etree.Element("XML")


        for i, record in enumerate(matched):
            #print i+1, record
            matched_root.append(record)

        for i, record in enumerate(docs_bilingual):
            #print i+1, record
            bilingual_root.append(record)
            
        for i, record in enumerate(unmatched):
            #print i+1, title, id
            unmatched_root.append(record[1])
            
        unmatched_outfile = "/Users/peder/dev/goc/LOAD/pilot-unmatched.xml"
        matched_outfile =  "/Users/peder/dev/goc/LOAD/pilot-matched.xml"
        bilingual_outfile =  "/Users/peder/dev/goc/LOAD/pilot-bilingual.xml"

    
        with open(unmatched_outfile,'w') as f:
            f.write(etree.tostring(unmatched_root))
            
        with open(bilingual_outfile,'w') as f:
            f.write(etree.tostring(bilingual_root))
        
        with open(matched_outfile,'w') as f:
            f.write(etree.tostring(matched_root))
    
    write_xml()  
            
    def report():

        f = open('unmatched.csv', 'wt')
        xf = open('unmatched.xml', 'w')
        writer = common.UnicodeWriter(f)
        writer.writerow(['No.','Department','ID','Name','Language'])

        for i,item in enumerate(unmatched):
            print item
            #print item[0]
            child = item[1]
            xf.write(etree.tostring(child))
            formid = child.xpath("FORM[NAME='thisformid']/A/text()")[0]
            title = item[0]
            try:
                dept_code=child.xpath("FORM[NAME='department']/A/text()")[0].split('|')[1]
                department= schema_description.dataset_field_by_id['owner_org']['choices_by_pilot_uuid'][dept_code]['eng']
            except:
                department = None
            
            writer.writerow([str(i),department, formid, title])
            
            
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

    
    
    def load_report_data():
        pass


def wrong_lang_fix():
    
    tree = etree.parse('unmatched.xml')
    #tree = etree.parse('put fixed.xml')
    root = tree.getroot()

    for i,child in enumerate(root):
       #print i
       title_elem = child.xpath("FORM[NAME='title_en']/A/text()")
       title=title_elem[0]  
       lang=language(child)

       for marker_en, marker_fr in common.language_markers:
           #if lang=="English": print ">>>>>>>>>>",lang,marker_en, marker_fr ,"\n" 
           if marker_en in title and lang=="French":
               #print i, lang, title

               #
               print etree.tostring(child)   
         
               break
       #print  i, lang, title
       #print etree.tostring(child)  

def wayward_duplicates():
    
    cnt=Counter()
    way = matched_ids()
    for w in way:
        cnt[w]+=1
        
    for i in list(cnt):
        print i[0] +","+i[1]
        
def force_bilingual():
    bi=[]
    with open('force-bilingual.csv', 'rb') as csvfile:
        for row in csv.reader(csvfile):
            bi.append(row[0].upper())
    return bi
            
def xml_report(file):
#    newroot = etree.Element("XML")
    from duplicates import duplicates
    tree = etree.parse(file)
    root = tree.getroot()
    found=[]
    
    cnt = Counter()
    pending_records=[]
    for i,child in enumerate(root):
       
        cnt["<RECORDS>"]+=1
        try:
            formid = child.xpath("FORM[NAME='thisformid']/A/text()")[0]
            if formid in duplicates:
                #do nothing
                cnt['duplicate']+=1
                if formid not in found:
                    found.append(formid)
                    cnt['found']+=1
                    #newroot.append(child)
            else:
                pass
                #newroot.append(child)
            #cnt["formid"]+=1
            #cnt[]
            #cnt[formid]+=1
        except:
            cnt["no formid"]+=1
            #print etree.tostring(child)
            
#    for i,child in enumerate(root):
#        try:
#            formid = child.xpath("FORM[NAME='thisformid']/A/text()")[0]
#        except:
#            pass
#        if formid in duplicates:
#            pass
#        else:
#            #newroot.append(child)
#            
    print found 
    for i in cnt.items():
        if i[1]>1:print i

#    outfile =  "/Users/peder/dev/goc/LOAD/pilot-problems/Combine-published-pending-no-duplicates.xml"
#    
#    with open(outfile,'w') as f:
#        f.write(etree.tostring(newroot))


def check_wrong_lang_fix():
    file = "/Users/peder/dev/goc/LOAD/pilot-problems/wrong-lang-fix2.xml"
    tree = etree.parse(file)
    root = tree.getroot() 
    
    for i,child in enumerate(root):   
        title_elem = child.xpath("FORM[NAME='title_en']/A/text()")
        title=title_elem[0]  
        lang=language(child) 
        print i,lang, title
        
if __name__ == "__main__":

    #pilot_file =  "/Users/peder/dev/goc/OD_DatasetDump-0-partial.xml" 
    finalfile="/Users/peder/dev/goc/LOAD/pilot-problems/final-final.xml"
    published_file="/Users/peder/dev/goc/PublishedOpendata-0.xml"
    pending_file="/Users/peder/dev/goc/PendingOpendata-0.xml"
    combined_file="/Users/peder/dev/goc/OpenData-Combined.xml"
    pending = "/Users/peder/dev/goc/LOAD/pilot-problems/pending.xml"
    combined1 = "/Users/peder/dev/goc/LOAD/pilot-problems/Combine-published-pending.xml"
    combined2 = "/Users/peder/dev/goc/LOAD/pilot-problems/Combine-published-pending-no-duplicates.xml"
    #find_pending(pending_file)
    split_xml_files(finalfile)
    #wrong_lang_fix()
    #check_wrong_lang_fix()
    #force_bilingual()
    #wayward_duplicates()
    #xml_report(combined2)

   