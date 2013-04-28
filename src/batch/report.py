# coding=utf-8
import os
import sys
import time
import json 
import csv
from lxml import etree
from collections import Counter
import common
import tabular as tb
from pprint import pprint
import logging
import argparse
from guess_language import guess_language
from ckanext.canada.metadata_schema import schema_description
#from pyPdf import PdfFileWriter
from pilot_model import PilotHoldings, PilotRecord

nspace = common.nrcan_namespaces
jl_dir = "/Users/peder/dev/goc/LOAD/"
class PilotReport:
    
    def __init__(self,datafile,report=False):
        # create instance of PilotData
        self.data = common.XmlStreamReader("RECORD",datafile)
    def full(self):
    
        X =tb.tabarray(columns = Cols2, names=['Region','Sector','Amount','Population'])
        print X
        
    def biligual_titles(self):
        cnt = Counter()
       
        for i,node in enumerate(self.data.elements()):

            try:
                titles = (node.xpath("FORM[NAME='title_en']/A/text()")[0],node.xpath("FORM[NAME='title_fr']/A/text()")[0])

                #print titles 
                language_markers = common.title_langauge_markers + common.title_langauge_markers_fra
                for marker in language_markers:
                    if marker in title:
                        en = title.replace(marker,'')
                        
                    elif marker in title_fra:
                        fra = title.replace(marker,'')
                    else:
                       pass
                print en,fra 
            except:
                raise 
            
            
    def clean_pilot_xml(self):
     
        cnt = Counter()
        file = open("/Users/peder/dev/goc/bilingual-pilot-records.xml", "w")
        file.write("<XML>\n")
        changed = 1
        for i,node in enumerate(self.data.elements()):
            
            title=''
            try:
                lang_code=''
                language=''
                title = node.xpath("FORM[NAME='title_en']/A/text()")[0]
                lang_code = node.xpath("FORM[NAME='language__']/A/text()")[0].split("|")[1]
                language = schema_description.dataset_field_by_id['language']['choices_by_pilot_uuid'][lang_code]['eng']
                print i, language
                cnt[language]+=1
                #print language
                if language == "Bilingual (English and French)":# or "ilingual" in title:
                    print "Bilingual ", ">>>", changed, i, language, title
                    cnt['cleaned'] +=1
                    changed+=1
                    file.write(etree.tostring(node) +"\n")                   
                 #root.append(node)   
                 #title = node.xpath("FORM[NAME='title_en']/A/text()")[0]
#                print language,title
#                #print language
#                cnt[language]+=1
#                department_code = node.xpath("FORM[NAME='department']/A/text()")[0].split("|")[1]
#                department = schema_description.dataset_field_by_id['owner_org']['choices_by_pilot_uuid'][department_code]['eng']
#                dept = department
#                #cnt[department]+=1
#                
            except  IndexError:
   
                #print node.xpath("FORM[NAME='language__']/A/text()")
                print "No Language ",changed,i, title
                changed+1
                
            except:
                raise

                #print "No Lang"
                #raise
            finally:
                pass
        file.write("</XML>")
        pprint(cnt.items())
            #bi_tree.write('/Users/peder/dev/goc/bilingual-pilot-records.xml', pretty_print=True, xml_declaration=False)
        
                
    def biligual_datasets(self):
        root = etree.Element("root")

        print etree.tostring(root, pretty_print=True, xml_declaration=True)
        sys.exit()
        # write to file:
        # tree = ET.ElementTree(root)
        # tree.write('output.xml', pretty_print=True, xml_declaration=True)

        cnt = Counter()
        dept =''
        title =''
        for i,node in enumerate(self.data.elements()):
           
            #print etree.tostring(node, pretty_print=True)
            try:
                
                lang_code = node.xpath("FORM[NAME='language__']/A/text()")[0].split("|")[1]
                language = schema_description.dataset_field_by_id['language']['choices_by_pilot_uuid'][lang_code]['eng']
#                if language == "Bilingual (English and French)":continue
                title = node.xpath("FORM[NAME='title_en']/A/text()")[0]
                print language,title
                #print language
                cnt[language]+=1
                department_code = node.xpath("FORM[NAME='department']/A/text()")[0].split("|")[1]
                department = schema_description.dataset_field_by_id['owner_org']['choices_by_pilot_uuid'][department_code]['eng']
                dept = department
                #cnt[department]+=1
                
            except:
                print "No Language ", title
                cnt[dept]+=1
                #print "No Lang"
                #raise
                
        pprint(cnt.items())
     
        
    def departments():  
        cnt = Counter()
        for i, node in enumerate(self.data.elements()):
            try:
            # Determine departments
            #node.xpath("DC.TITLE/text()")
                uuid = node.xpath("DEPARTMENT/text()")[0].split("|")[1]
                
                dept =schema_description.dataset_field_by_id['author']['choices_by_pilot_uuid'][uuid]['key']
                print dept
                cnt[dept] += 1
                
            except IndexError:
                print node.xpath("DEPARTMENT/text()")
                cnt['none'] +=1
            
        for i in sorted(cnt.items()):
            print "{}, {}".format(i[0].split("|")[0], i[1])
        
    def unique_fields(self):
        counter = 0
        unique_form_id = 0        
        for doc in self.data.elements():
            
            self.report.write(str(counter)+"\n")    

class NapReport:
    nspace = {'gmd': 'http://www.isotc211.org/2005/gmd','gco':'http://www.isotc211.org/2005/gco','gml':'http://www.opengis.net/gml'}   
    logging.basicConfig(filename="/Users/peder/dev/goc/ckan-logs/report.log", level=logging.INFO)
    def __init__(self,path):
        ''' determine if it's a file or folder '''
        self.filedir = path

        
    def _xml_generator(self, filedir):
        '''
            walk through nap files in en and fr folders and extract xml
        '''
        basepath = filedir
        for (path, dirs, files) in os.walk(os.path.normpath(filedir+"/en")):
                for n, file in enumerate(files):
                    # All non nap files should be ignored
                    if ".nap" not in file:continue
                    en = open(os.path.join(path,file),"r")
                    try:
                        fr = open(os.path.join(filedir+"/fr",file),"r")
                    except IOError:
                        logging.error(file)
                        continue
                    doc_en = etree.parse(en)
                    doc_fr = etree.parse(fr)
                    yield doc_en,doc_fr
    def pathstring(key):
            return doc.xpath(('//gmd:%s/gco:CharacterString' % key),namespaces=nspace)[0].text
    def resource_urls(self):
        print "Reporting on various resource urls to find overlap "
        xml_gen = self._xml_generator(self.filedir)
        
        for n,docs in enumerate(xml_gen):
            print "---------- {} ----------".format(n)

            try:
                
                resources = (docs[0].xpath('//gmd:CI_OnlineResource',namespaces=nspace),docs[1].xpath('//gmd:CI_OnlineResource',namespaces=nspace))
               
                for r in resources:
                    print r[0].find('gmd:linkage/gmd:URL', nspace).text
                    print r[1].find('gmd:linkage/gmd:URL', nspace).text
                
            except Exception as e:
                print e
    def author_email_count(self):
        print "Reporting on various resource urls to find overlap "
        xml_gen = self._xml_generator(self.filedir)
        
        for n,docs in enumerate(xml_gen):
            try:
                
                resources = (docs[0].xpath('//gmd:CI_OnlineResource',namespaces=nspace),docs[1].xpath('//gmd:CI_OnlineResource',namespaces=nspace))
               
                for r in resources:
                    print r[0].find('gmd:linkage/gmd:URL', nspace).text
                    print r[1].find('gmd:linkage/gmd:URL', nspace).text
                
            except Exception as e:
                print e  
                         
    def bilingual_title_count(self):
       
        ''' How many titles have been translated '''
        xml_gen = self._xml_generator(self.filedir)
        cnt = Counter()
        
        for n,docs in enumerate(xml_gen):
            if n % 1000 == 0: print n
            #if n > 10000: break;
            try:

                email = docs[0].xpath('//gmd:electronicMailAddress/gco:CharacterString',namespaces=nspace)
                
                if titles[0][0].text == titles[1][0].text:
                    cnt['unilingual']+=1
                else:
                   cnt['bilingual']+=1 
                
            except Exception as e:
                print e                   
        
        print cnt
        
    def resource_languages(self):
        ''' what are the languages of the datasets? '''
        xml_gen = self._xml_generator(self.filedir)
        cnt = Counter()
        
        for n,docs in enumerate(xml_gen):
            if n % 1000 == 0: print n
            try:
                languages = (docs[0].xpath('//gmd:MD_DataIdentification/gmd:language/gco:CharacterString',namespaces=nspace),docs[1].xpath('//gmd:MD_DataIdentification/gmd:language/gco:CharacterString',namespaces=nspace))
                lang_str = "%s, %s" % (languages[0][0].text,languages[1][0].text)
                cnt[lang_str]+=1
                
            except Exception as e:
                print e                       
        
        print cnt
    
    def resource_formats(self):
        #report = open(os.path.normpath('/temp/reports/filetypes.txt'), 'w')
        total = 0
        image_format_types = []
        all_format_types=[]
        known_format_types=[]
        unknown_format_types=[]

        all_cnt  = Counter()
        known_cnt  = Counter()
        unknown_cnt = Counter()
        image_cnt = Counter()
        
        for (path, dirs, files) in os.walk(os.path.normpath(self.filedir)):
            for n, file in enumerate(files):
                f = open(os.path.join(path,file),"r")
                doc = etree.parse(f)
                fmt = doc.find('//gmd:MD_Format/gmd:name/gco:CharacterString',nspace).text
                all_format_types.append(fmt)


                resources=doc.xpath('//gmd:CI_OnlineResource',namespaces=nspace)

                for r in resources:
              
                    try:
                        if in_schema_formats(fmt): 
                            known_format_types.append(fmt)
                            #print n,r.find('gmd:name/gco:CharacterString', nspace).text, r.find('gmd:linkage/gmd:URL', nspace).text
                            #"/gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributionFormat/gmd:MD_Format/gmd:name/gco:CharacterString"
                            pass
                        else:
                            unknown_format_types.append(fmt)
                            pass
                            
                    except:                        
                        pass
    
                if (n % 100) == 0: print n 

          
            for a in all_format_types:
                all_cnt[a] +=1
            for k in known_format_types:
                known_cnt[k] +=1
            for u in unknown_format_types:
                unknown_cnt[u] +=1
                
            counter_to_markdown_table("All Geogratis Formats", all_cnt)
            counter_to_markdown_table("Known Schema Formats", known_cnt)
            counter_to_markdown_table("Uknown Geogratis Formats", unknown_cnt)
            
            print "TOTAL ", sum(all_cnt.values() + known_cnt.values() + unknown_cnt.values())
                
        
    def pathtype(path):
        
        if os.path.isdir(path) == True:
            print path, "is a dir  (created", asciiTime, ")"
            list_files(path)
        else:   
            asciiTime = time.asctime( time.gmtime( created ) )
            print d, "is a file (created", asciiTime, ")"
        self.filedir = filepath
        
    def list_files(startpath):
        ''' Nested listing files and dirs '''
        for root, dirs, files in os.walk(startpath):
            level = root.replace(startpath, '').count(os.sep)
            indent = ' ' * 4 * (level)
            print('{}{}/'.format(indent, os.path.basename(root)))
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                print('{}{}'.format(subindent, f))
            
    def _read(self):
         cnt = Counter()
         for (path, dirs, files) in os.walk(os.path.normpath(self.filedir)):
            for num, file in enumerate(files):
                #print num+1, file
                f = open(os.path.normpath(path + "/" + file), "r")
                doc = etree.parse(f)
                try:
                    for k in keywords_by_code(doc,"RI_525",self.nspace):
                        cnt[k]+=1
#                    for k in keywords_by_code(doc,"RI_528",self.nspace):
#                        cnt[k]+=1
                    
                except NestedKeyword as n:
                    print "THERE IS A NESTED KEYWORD SO LOG IT "
                    print "Args ", n.args
                    continue
                except IndexError:
                    print "Codes RI_525 or RI_525 not present"
                except EmptyKeyword:
                    print "No Tags"
                
         pprint(cnt.items())
                
         pass



    
def count_occurances(dir, pathlist):
    """
        Return a report of counts of various NAP file elements
        
        param dir: Folder containing NAP files
        param pathlist:  A list of XPath elements to be counted
    
    """
    
    cnt = Counter()
    docs = common.xml_generator(dir)
    for doc in docs:
        for path in pathlist:
            try:
                val = doc.find(path, nspace).text
                cnt[val]+=1
            except AttributeError:
                print path, doc.find("//gmd:fileIdentifier/gco:CharacterString", nspace).text        
    
    for item,count in cnt.items():
        print item, count

def write_csv(pilot_file):
    
    csvout = "/Users/peder/dev/goc/pilot.csv"
    f = open(csvout, 'wt')
    writer = common.UnicodeWriter(f)#csv.writer(f)
    fields = sorted(tuple(schema_description.all_package_fields ))
    fields2 = [ x for x in fields if "name" not in x ]
    
    fields3 = list(fields2)
    
    for x in range(1,4):
        fields3.append('resource_url_%s' % x)
        fields3.append('resource_url_format_%s' % x)
        fields3.append('resource_language_%s' % x)
        fields3.append('resource_resource_type_%s' % x)

    writer.writerow(fields3)

    file = open(os.path.normpath(pilot_file),"r")
    
    for line in file:
        
        record = json.loads(line)
        row =[]
        
        for i,field in enumerate(fields2):
           
            try:
                
                val=record[field]
                row.append(val)
                
            except Exception as e:

                raise
        resources = record['resources']
        for r in resources:

            for val in r.values():
                row.append(val)

        writer.writerow(row)

    f.close()

def jl_test(nrcanjl_path):
    print os.path.normpath(nrcanjl_path)
    file = open(os.path.normpath(nrcanjl_path),"r")
    cnt = Counter()

    print file
    for i,line in enumerate(file):

        record = json.loads(line)
        
        if "Abstract not available - " in  record['notes']:
            cnt['dash'] +=1
        elif "This series is produced to expedite the release of information" in record['notes']:
            cnt['full'] +=1
            print record['notes'].split('This series is produced to expedite the release of information')[0]
            print record['notes_fra']
            sys.exit()
        elif record['notes'] == "Abstract not available." :
           
            cnt['small'] +=1
            #print record['notes']
            #if i>50: sys.exit()
            try:
                pass
                #print record['notes'].split(' - ')[0]
            except:
                pass
                #print record['notes']
        #print [record[ckan_name] for (ckan_name, pilot_name, field) in schema_description.dataset_all_fields()]
        # test to see if there are resources
        #print record['resources'] 
        #print (schema_description.all_package_fields - schema_description.extra_package_fields)
        
        
                #print "Does not exist"
        #sys.exit()
    print cnt.items()

# Find latests .jl file
def newest_jl(dir,type):
    jl_files = sorted([f for f in os.listdir(dir) if f.startswith(type)])
    return  dir + jl_files[-1]        


class PilotDelegator:
    """
        To work with pilot data, its best for first create
        the data in memore for later manipulation rather than reading it 
        again and again from the xml.
        
        When dealing with a collection of records, encapsulation is very useful:
        I only want to know that a record has been created and validated, and that
        if it fails to do so, that I'm alerted so I can log it. 

    
    """
    cnt = Counter()
    def __init__(self, datafile):
        self.holdings = PilotHoldings()
        self.data = common.XmlStreamReader("RECORD",datafile)
        for i,node in enumerate(self.data.elements()):
            
            try:
                self.holdings.add_record(node)
            except Exception  as e:
                # this is where logging belongs
                print "----------Error------------"
                print e.message
                print e.node
                print "----------Error End---------"
                self.cnt[e.message]+=1
        print cnt.items()
        #self.holdings.pickle_it()
    def report(self):
        self.holdings.report('full')
    def test(self):
        # This will fail, so we must alther the holdings to make it pass
        self.holdings.test() 
    
if __name__ == "__main__":

    #/Users/peder/dev/goc/LOAD/
        
    print "Report"
    pilot_file =  "/Users/peder/dev/goc/OD_DatasetDump-0.xml" 
    pilot = PilotDelegator(pilot_file)
    pilot.report()
   
    
    #path = os.path.normpath("/Users/peder/dev/goc/nap/en")
    nap_path = os.path.normpath("/Users/peder/dev/goc/nap")
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('source', help='Which data source', action='store',choices=['pilot', 'geogratis','nrcan-jl','pilot-jl'])
    parser.add_argument('action', help='What type of report', action='store',choices=['titles', 'short','counts','titles','full','test','csv'])
    parser.add_argument("-p", "--path", help="file or dir", action='store_true')

    #args = parser.parse_args()
    
    if args.source == 'pilot' and args.action == 'titles':
        PilotReport(pilot_file).biligual_titles()
    
    elif args.source == 'pilot' and args.action == 'full':
        PilotReport(pilot_file).full()
       #pilot_report()
       
    elif args.source == 'geogratis' and args.action == 'counts':
        pathlist = ['//gmd:electronicMailAddress/gco:CharacterString',
                    '//gmd:MD_MaintenanceFrequencyCode',
                    '//gml:begin/gml:TimeInstant/gml:timePosition']
        count_occurances('/Users/peder/dev/goc/nap-sample/en',pathlist)
    
    elif args.action == 'titles':
       NapReport(nap_path).bilingual_title_count()  
       
    elif args.source == 'nrcan-jl':
         if args.action == 'test': jl_test(newest_jl(jl_dir,'nrcan'))

    elif args.source == 'pilot-jl':  
        jl_file = newest_jl(jl_dir,'pilot')  
        if   args.action == 'csv':write_csv(jl_file)
        elif args.action == 'report':pilot.report()
        elif args.action == 'test':pilot.test()

 