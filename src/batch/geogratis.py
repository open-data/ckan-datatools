# Inspired by https://github.com/okfn/ckanext-pdeu/blob/master/ckanext/pdeu/harvesters/digitaliser_dk.py

''' This module is used to read data from the Geogratis web services into two master data files, 
    one in english and one in french.
    Then tools are provided to generate reports on the data and import it into CKAN  etc. '''

from lxml import etree
import urllib2
import os
import json
from pprint import pprint
import sys
from pprint import pprint
import time
import socket 
from itertools import *
import argparse
from lxml import etree
import fileinput
        
NEXT = "http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/?alt=json&max-results=50"
LAST_REQUEST =''
def gather_products():
    global total_download
    global LAST_REQUEST
    global NEXT
    #if LAST!='':NEXT="http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/?alt=json&max-results=50&start-index=%s" % LAST_REQUEST

    total_download = 0

    data = []
    opener = urllib2.build_opener()
    while True:
        
        
        try:
            req = urllib2.Request(NEXT+'&alt=json')
            f = opener.open(req,timeout=500)
            #print req.has_header('Content-Length')

        except urllib2.URLError:
            #start again where we left off
            # or I could just wait for 5 min, then try 
            # f = opener.open(req,timeout=300) again
            #gather_stage(LAST_REQUEST)
            req = urllib2.Request(NEXT+'&alt=json')
            f = opener.open(req,timeout=50)
        except socket.timeout:
            print "socket timeout"
            
        response = f.read()
    
        json_response = json.loads(str(response),"utf-8")
        
        # Get the link to the next batch of links
        links = json_response['links']
        for  link in links:
            if link['rel']=='next': 
                NEXT = link['href'] 
                LAST_REQUEST=NEXT
                break

        for product in json_response['products']:     
            file.write(product);  
            file.write(",")
    pass

def test_single():   
    json_data=open('data/nrcan-single.json')
    data=json.load(json_data)
    create_package(data)
    

def api_call(payload):
    pprint(json.dumps(payload))
    headers = {'Authorization': 'tester'}
    url = u"http://localhost:8080/api/action/package_create"
    headers = {'Authorization': 'tester','content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    print r.status_code
    
def crossReference(fname1,fname2,outfile):
    def findit(id):
        with open(fname2, 'r') as inF:
            for line in inF:
                if id in line:
                    return line

    out = open(outfile, "w")
    x =0
    with open(fname1) as infile:
        for i,line in enumerate(infile):    
            fr = findit(json.loads(line)['id'])
            tup = (i, json.loads(line), json.loads(fr))
            out.write(str(tup) + "\n")
            x+=1
            if x > 2:break
    

        infile.close()
        out.close()
        inF.close()
        '''
        from itertools import izip
        with open(fname1) as f1:
            with open(fname2) as f2:
                for (c1, c2) in izip(f1, car_names(f2)):
                    print c1, c2 
        '''      

class NrcanMunge():
    def __init__(self):
        
        pass
 
    def mungeDatasets(self):
        
        with open('/Users/peder/dev/goc/nrcan.links', 'r') as inF:
            for line in inF:
                fr, en = str(line).strip().split(", ")
                print fr, en
                sys.exit()
        self.out.close()   

  
    def create_ckan_data(self):
        ''' Create NRCAN datasets in CKAN format and insert into database '''
        config = SafeConfigParser()
        config.read('nrcan.config')
        opener = urllib2.build_opener()
        
        infile = open('/Users/peder/dev/goc/nrcan.links', "r")
        #outfile = open('/Users/peder/dev/goc/nrcan.dat', "w")
        for line in infile:
            links = str(line).strip("\n").split(', ')
            req = urllib2.Request(links[0])  
            try: 
                f = opener.open(req,timeout=5)
            except socket.timeout:
                print "socket timeout"
            
            response = f.read() 
            data = json.loads(response)
            db = NrcanDb()         
            db.insert(self, json.loads(data))              
            sys.exit()
            pass
    def strip_whitespace(self):
        filename_in = os.path.normpath('/temp/nrcan.dat')
        filename_out = os.path.normpath('/temp/nrcan-strip2.dat')
        outfile =  open(filename_out, "a");
        with open(filename_in) as infile:
            for line in infile:
                if not line.rstrip():
                    continue
                else:
                   outfile.write(line.rstrip())
                   
                   
    def count_lines(self):
        c=0
        path = os.path.normpath('/temp/nrcan-strip.dat')
        with open(path, "r") as infile:
        
           for line in infile:
               c+=1
               if c > 43098700:
                   print line
        print c
            
    def write_new_links(self): 
        infile = open(os.path.normpath('/temp/nrcan2.links'), "r")   
        links = open(os.path.normpath('/temp/nrcan3.links'), "w")
        start = False
        for line in infile:
            en, fr = str(line).strip().split(', ')
            if start:
                print "WRITE", en
                links.write(line)
            elif en == "http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/56bb6177-1364-4fe3-8515-16d94dcef79f.nap":
                start = True
            else:
                print "SKIP", en
            
    def save_nrcan_data(self):
        ''' Grab NRCan Data and dump into a file '''
        opener = urllib2.build_opener()
        
        
        outfile = open(os.path.normpath('/temp/nrcan3.dat'), "w")
        do = False
        for line in infile:
            en, fr = str(line).strip().split(', ')
            print en 
            if do: 
                req = urllib2.Request(en)  
                try: 
                    f = opener.open(req,timeout=500)
                except socket.timeout:
                    print "en socket timeout"
                data_en = f.read() 
                
                req = urllib2.Request(fr)  
                try: 
                    f = opener.open(req,timeout=500)
                except socket.timeout:
                    print "fr socket timeout"
                data_fr = f.read() 
           
                outfile.write(str(data_en) + "|||" + str(data_fr) + "\n")
            else:
                
                if en == "http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/56bb6177-1364-4fe3-8515-16d94dcef79f.nap":
                   do = True
                else:
                    line.strip()
            pass
        
            
    def read_nrcan_data(self):
           ''' Read links from enercan and save them into bilinguages dataset file or database '''
           config = SafeConfigParser()
           config.read('nrcan.config')
           opener = urllib2.build_opener()
           infile = open(os.normpath('/temp/nrcan.links', "r"))
           outfile = open(os.normpath('/temp/nrcan.dat', "w"))
           for line in infile:
               links = str(line).strip("\n").split(', ')
               req = urllib2.Request(links[0])  
               try: 
                   f = opener.open(req,timeout=50)
               except socket.timeout:
                   print "socket timeout"
               package_dict = {'extras': {}, 'resources': [], 'tags': []}
               response = f.read() 
               n = json.loads(response)
               # create english fields
    
               for ckan, nrcan in config.items('package'):
                   if nrcan == "SELECT":
                      print "SELECT"
                      package_dict[ckan] = schema_description.dataset_field_by_id[ckan]['choices'][1]['key']
                   elif "$." in nrcan:
                       print "Use JSON Path"
                       print nrcan
                       print jsonpath(n, nrcan)
                   elif nrcan:
                       print n[nrcan]
                       package_dict[ckan] = n[nrcan]
    
               pprint(package_dict)
    
               sys.exit()
               pass
    
if __name__ == "__main__":
    #report("/Users/peder/dev/goc/nrcan.jl","/Users/peder/dev/goc/nrcan2-fr.jl","/Users/peder/dev/goc/nrcan-combined.txt")
    #test_single()
    NrcanMunge().count_lines()
    '''
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action='store_true')
    parser.add_argument('action', help='The Action you wish to perform on the data', action='store',choices=['init','list','update','report'])
    parser.add_argument('entity', help='The data entity you wish to operate on', action='store',choices=['org','group','user','pack'])
      
    args = parser.parse_args()
    print args
    '''
 

        

