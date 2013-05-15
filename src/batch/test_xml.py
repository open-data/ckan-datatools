from datetime import date
import json
from collections import Counter
from lxml import etree
import common
import pickle
langcodes={'D892EF88-739B-43DE-BDAF-B7AB01C35B30':'English',
           'FA6486B4-8A2A-4DA4-A727-E4EA3D29BF71':'French',
           '790CE47F-0B49-4D1F-9CE0-50EC57517981':'Bilingual'
           }

def language(record):
    
    try:
        language__ = record.xpath("FORM[NAME='language__']/A") 
        if language__:
            language = language__
        else:
            language = record.xpath("FORM[NAME='language']/A")

        langcode=language[0].text
        if langcode: 
            langcode = langcode.split('|')[1]
            return langcodes[langcode]
    except:
        
        raise

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
            lang=language(child)
            if lang=="Bilingual":
                ids_source.append(formid)
        except:
            print "small NO Language"
    
            
       
            
        
    biset= set(ids_bi)
    fullset = set(ids_source)
    print biset.issubset(fullset)
    diff = fullset.difference(biset)
    print diff
    
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
    find_missing_bilingual(bilingual_file,final)
    
    #xml_rescue(combined2)
