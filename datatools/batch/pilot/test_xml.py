from datetime import date
import json
from collections import Counter
from lxml import etree
import datatools.batch.common
import pickle
from pprint import pprint




def xml_records(file):
    

    tree = etree.parse(file)
    root = tree.getroot()
    
    xrecords=[]

    for child in root:
       try:
           formid = child.xpath("FORM[NAME='thisformid']/A/text()")[0]
           title = child.xpath("FORM[NAME='title_en']/A/text()")[0]
        
           xrecords.append(child)
           
       except:
           #raise
           print "bad record"
           
    return xrecords
#    pickle.dump(xrecords, open('xrecords.pkl','wb'))

def xml_rescue(file):
    
    diff = pickle.load(open('diff.pkl','rb'))
    cnt=Counter()
    tree = etree.parse(file)
    #tree = etree.parse('put fixed.xml')
    root = tree.getroot()
    print diff
    rescued=[]

    for i,child in enumerate(root):
        try:
            formid = str(child.xpath("FORM[NAME='thisformid']/A/text()")[0]).lower()
            if formid in diff:
                print "FOUND ONE", formid
        except:
            print "Weird", formid

def find_missing_bilingual(file1,file2):
    cnt=Counter()
    tree1 = etree.parse(file1)
    tree2 = etree.parse(file2)
    root1 = tree1.getroot()
    root2 = tree2.getroot()
    ids_bi=[]
    ids_source=[]
    
    for i,child in enumerate(root1):
        
        try:
            formid = str(child.xpath("FORM[NAME='thisformid']/A/text()")[0]).lower()
        except:
            print "SMALL NO FORM ID"
        try:
            lang=language(child)
            if lang=="Bilingual":
                ids_bi.append(formid)
        except:
            print "small NO Language"
               
    for i,child in enumerate(root2):
        try:
            formid = str(child.xpath("FORM[NAME='thisformid']/A/text()")[0]).lower()
        except:
            print "BIG NO FORM ID"
            print child.find("DC.TITLE").text
            print child.xpath("FORM[NAME='title_en']/A/text()")
            #print etree.tostring(child)
        try:
            lang=common.language(child)
            if lang=="Bilingual":
                ids_source.append(formid)
        except:
            print "small NO Language"  
        
    biset= set(ids_bi)
    fullset = set(ids_source)
    print biset.issubset(fullset)
    diff = fullset.difference(biset)
    print diff

def pending_ids(file):
    
    tree = etree.parse(file)
    #tree = etree.parse('put fixed.xml')
    root = tree.getroot()
    
    pending=[]
    for i,child in enumerate(root):
       
       try:
           formid = child.xpath("FORM[NAME='thisformid']/A/text()")[0]
           pending.append(formid.lower())
           
           #xrecords.append((str(lang),str(formid)))
           
       except:
           raise
       
    pprint(pending)

def check_language(file):
    ''' test to make sure all not_in_new files crept into jl files becaues of order problem
        because they are actually french (no french ids should be in the .jl file)  
    '''
    not_in_new = pickle.load(open('not_in_new.pkl','rb'))
    final  = etree.parse(file).getroot()

    for i,child in enumerate(final):
        try:
            formid = str(child.xpath("FORM[NAME='thisformid']/A/text()")[0]).lower()
            if formid in not_in_new:
                print common.language(child)
        except IndexError:
            print "SMALL NO FORM ID", child.xpath("FORM[NAME='thisformid']/A/text()")
            #raise
    print "Conlusion, all records have french primary ids, and thus must be removed"


def cansim_summary(xml):
    
    file1="/Users/peder/dev/OpenData/cansim/opendcansim08.json"  
    file2="/Users/peder/dev/OpenData/cansim/opendsumtab08.json"
    sum_ids=[]
    
    def process(file):
        lines = [line.strip() for line in open(file)]
        for  i,line in enumerate(lines):
            package = json.loads(line)
            sum_ids.append(package['id'])
            
    process(file1)
    process(file2)
    
    print len(sum_ids)
    
    registry=xml_records(xml)
    
  
    patterns=['www5.',
              'www.statcan.gc.ca/tables-tableaux/sum-som',
              'www12.statcan.gc.ca/census-recensement/2011/geo',
              'geodepot.statcan.gc.ca']
    
    delete=[]
    for i,child in enumerate(registry):
        delete_flag=False
        formid = child.xpath("FORM[NAME='thisformid']/A/text()")[0]
        try:
            program_page_en = child.xpath("FORM[NAME='program_page_en']/A/text()")[0]
            program_url_fr = child.xpath("FORM[NAME='program_url_fr']/A/text()")[0]

            
            for p in patterns:
                if p in program_page_en:
                    delete.append(formid)
                    break
        
                    
        except:
            print i,"--------none ----------"

           
        

    
    print len(delete)
    
    print len(set(delete).difference(set(sum_ids)))
    print len(set(sum_ids).difference(set(delete)))        
 
    print "Conlusion:  This report does not work with XML file because it does not have merged files, which is a requisite"
      
    '''
    page url patterns for CANSIM and Summary Tables:
     
    CANSIM
    http://www5.
     
    Summary Tables
    http://www.statcan.gc.ca/tables-tableaux/sum-som
    
    Geography Division 2011
    http://www12.statcan.gc.ca/census-recensement/2011/geo.....
     
    Geography Division 2006
    http://geodepot.statcan.gc.ca.....
    '''
  
if __name__ == "__main__":

    load_dir = '/Users/peder/dev/goc/LOAD'
    published_file="/Users/peder/dev/goc/PublishedOpendata-0.xml"
    pending_file="/Users/peder/dev/goc/PendingOpendata-0.xml"
    combined_file="/Users/peder/dev/goc/OpenData-Combined.xml"
    pending = "/Users/peder/dev/goc/LOAD/pilot-problems/pending.xml"
    combined1 = "/Users/peder/dev/goc/LOAD/pilot-problems/Combine-published-pending.xml"
    combined2 = "/Users/peder/dev/goc/LOAD/pilot-problems/Combine-published-pending-no-duplicates.xml"
    final = "/Users/peder/dev/goc/LOAD/pilot-problems/final-final.xml"
    bilingual_file =  "/Users/peder/dev/goc/LOAD/pilot-bilingual.xml"
    cansim_summary(final)
