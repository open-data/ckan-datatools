from datetime import date
import json
from collections import Counter
from lxml import etree
import datatools.batch.common
import pickle
from pprint import pprint




def xml_report(file):
    
    cnt=Counter()
    tree = etree.parse(file)
    #tree = etree.parse('put fixed.xml')
    root = tree.getroot()
    
    xrecords=[]

    for i,child in enumerate(root):
       try:
           formid = child.xpath("FORM[NAME='thisformid']/A/text()")[0]
           title = child.xpath("FORM[NAME='title_en']/A/text()")[0]
           lang=language(child)
           cnt[lang]+=1
           
           #xrecords.append((str(lang),str(formid)))
           
       except:
           cnt['bad record']+=1
           
    for i in cnt.items():
        print i
    #print xrecords
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
#    print ">>> PublishedOpendata-0.xml"
#    xml_report(published_file)
#    print ">>> Published with pending"
#    xml_report(combined2)
#    print ">>> 'Manual' additions"
#    xml_report(final)
#    print ">>> Bilingual XML"
#    find_missing_bilingual(bilingual_file,final)
#    check_language(final)
    pending_ids(pending)
    #xml_rescue(combined2)
