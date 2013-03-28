import os
import sys
import time
from lxml import etree
from collections import Counter
import common
from pprint import pprint
#from pyPdf import PdfFileWriter

nspace = common.nrcan_namespaces

class NapReport:
    nspace = {'gmd': 'http://www.isotc211.org/2005/gmd','gco':'http://www.isotc211.org/2005/gco','gml':'http://www.opengis.net/gml'}   

    def __init__(self,path):
        ''' determine if it's a file or folder '''
        self.filedir = path
        #self._read()
        #self.minireport()
        self.resource_formats()
        
    def minireport(self):
#        path, dirs, files = os.walk("/usr/lib").next()
#        file_count = len(files)
#        print len([name for name in os.listdir('.') if os.path.isfile(name)])
        total = 0
        cnt = Counter()
        for (path, dirs, files) in os.walk(os.path.normpath(self.filedir)):
            for n, file in enumerate(files):
                #cnt[file] += 1
                total = n
        print "Number of files ", total
    
    def resource_formats(self):
        #report = open(os.path.normpath('/temp/reports/filetypes.txt'), 'w')
        total = 0
        all_format_types=[]
        known_format_types=[]
        unknown_format_types=[]

        all_cnt  = Counter()
        known_cnt  = Counter()
        unknown_cnt = Counter()
        
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
                #if n > 1000: break
          
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

def counter_to_markdown_table(header,counter):
    table = "|%s        |   Number   |\n|:-------------|-----------:|\n" % header
    for item in counter.items():
        row ="|%s|%s|\n" % (item[0], item[1])
        table+=row
        
    print table
    
    

if __name__ == "__main__":
    pprint (common.schema_file_formats)
    fmt=''
    for f in common.schema_file_formats:
      fmt += f+", "
    print fmt
    #NapReport(os.path.normpath("/Users/peder/dev/goc/nap/en"))       
    '''
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('action', help='What type of report', action='store',choices=['full', 'short'])
    parser.add_argument("-p", "--path", help="file or dir", action='store_true')

    args = parser.parse_args()
    
    if args.action == 'full':
       NapReport(args.path)
    
 
    You may want to do this interactively to warn of extended processing time for 
    certain files and dirs

    if get_valid_input("What do you want to do?", ("report","build")) == 'report':
        path = os.path.normpath(raw_input("Enter file or path: "))
        stat = os.stat(path)
        created = os.stat(path).st_mtime
        asciiTime = time.asctime( time.gmtime( created ) )
        if os.path.isdir(path) == True:
            print path, "is a dir  (created", asciiTime, ")"
            list_files(path)
        else:   
            asciiTime = time.asctime( time.gmtime( created ) )
            print d, "is a file (created", asciiTime, ")"

    '''