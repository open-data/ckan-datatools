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

nspace = common.nrcan_namespaces

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
                
#                [f() for marker in language_markers if marker in titles[0:1]]
#                    if marker in titles:
#                        print marker
#                        new_titles = (titles[0].replace(marker, ''),titles[1].replace(marker,''))
#                        print new_titles
            
            except IndexError as e:
                print  "INDEX ERROR ", node.xpath("FORM[NAME='title_en']/A/text()")
                cnt['None']+=1
            except Exception as e:
                print e
                raise   
        #pprint(cnt.items())
     
        
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
    writer = csv.writer(f)
    fields = sorted(tuple(schema_description.all_package_fields ))
    writer.writerow(fields)

    file = open(os.path.normpath(pilot_file),"r")
    
    for line in file:
        
        record = json.loads(line)
        # test to see if there are resources
        #print record['resources'] 
        #print (schema_description.all_package_fields - schema_description.extra_package_fields)
        row =[]
        for field in fields:
            
            try:
                
                val=record[field]
                row.append(val)
                
            
                
            except Exception as e:
                print e
            
        print row
        writer.writerow(row)
        sys.exit()
  
        f.close()

def jl_test(nrcanjl_path):
    
    file = open(os.path.normpath(nrcanjl_path),"r")
    for line in file:
        record = json.loads(line)
        # test to see if there are resources
        #print record['resources'] 
        #print (schema_description.all_package_fields - schema_description.extra_package_fields)
        for ckan_name, pilot_name, field in schema_description.dataset_all_fields():
            try:
               
                if pilot_name:
                 
                    print">>>", pilot_name ,"::", record[ckan_name]
                
            except KeyError:
                pass
                #print "Does not exist"
        sys.exit()
if __name__ == "__main__":
    print "Report"
    pilot_file =  "/Users/peder/dev/goc/OD_DatasetDump-0.xml" 
    #path = os.path.normpath("/Users/peder/dev/goc/nap/en")
    nap_path = os.path.normpath("/Users/peder/dev/goc/nap")
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('source', help='Which data source', action='store',choices=['pilot', 'geogratis','nrcan-jl','pilot-jl'])
    parser.add_argument('action', help='What type of report', action='store',choices=['titles', 'short','counts','titles','full','test','csv'])
    parser.add_argument("-p", "--path", help="file or dir", action='store_true')

    args = parser.parse_args()
    
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
       
    elif args.source == 'nrcan-jl' and args.action == 'test':
        nrcanjl_file = "/Users/peder/dev/goc/LOAD/nrcan-full-2013-04-24.jl"
        jl_test(nrcanjl_file)
    
    elif args.source == 'pilot-jl' and args.action == 'csv':
        pilot_file = "/Users/peder/dev/goc/LOAD/pilot-2013-04-24.jl"
        write_csv(pilot_file)

 