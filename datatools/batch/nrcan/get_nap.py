#-*- coding:UTF-8 -*-
import os
import json
import time
import socket 
import warnings
import urllib2
from pprint import pprint
import urlparse

NEXT = "http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/?alt=json&max-results=50&start-index=1209637"
LAST_REQUEST =''

def gather_products():
    linkfile ="/Users/peder/dev/goc/LOAD/products-may17.links"
    file = open(os.path.normpath(linkfile), "a")
    global total_download
    global LAST_REQUEST
    global NEXT
    #LAST_REQUEST="http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/?alt=json&max-results=50&start-index=%s" % 1306660
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
            # or  wait for 5 min, then try 
            # f = opener.open(req,timeout=300) again
            #gather_stage(LAST_REQUEST)
            req = urllib2.Request(NEXT+'&alt=json')
            f = opener.open(req,timeout=50)
        except socket.timeout:
            print "socket timeout"
            
        response = f.read()
        json_response = json.loads(str(response),"utf-8")
        
        # Get the link to the next batch of links
        #  This is a hack, it should be replaced by constructing a url from 
        # the last updateIndex (see below)
        
        links = json_response['links']
        for  link in links:
            if link['rel']=='next': 
                NEXT = link['href'] 
                LAST_REQUEST=NEXT
                break
        
       
        
        # GO UNTIL http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/?start-index=946000&max-results=50
        for product in json_response['products']:  
            updateIndex=product['updateIndex']
          
            file.write(product['id'] + "\n");  
 
        print "--------------- {} --------------".format(updateIndex)
        if int(updateIndex)<946000:
            file.close()
            sys.exit()


def download_nap(linkfile,outpath):
    
        """
        A simple funtion to fetch .nap files from Geogratis.
    
            :param linkfile: A file with a list of links to nap files. Example: 
                             http://geogratis.gc.ca/api/fr/nrcan-rncan/ess-sst/16d4b644-6ba0-4893-b85e-c5c883f1b875.nap
            :param outpath:  The local path in which to store .nap files
            
        """
        
        infile = open(os.path.normpath(linkfile), "r")

        for line in infile:
                print line
                req = urllib2.Request(line)  
                try: 
                    f = urllib2.urlopen(req,timeout=500)
                    data = f.read()
   
                    napfile = open(os.path.normpath('%s/%s' % (outpath,filename), "w"))
                    napfile.write(data)
                    napfile.close()
                except urllib2.HTTPError as h:
                    print h   
                except socket.timeout as s:
                    print s    


# --------------------- OLD ----------------------


       
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
 

def download_nap(linkfile,outpath):
    
        """
        A simple funtion to fetch .nap files from Geogratis.
    
            :param linkfile: A file with a list of links to nap files. Example: 
                             http://geogratis.gc.ca/api/fr/nrcan-rncan/ess-sst/16d4b644-6ba0-4893-b85e-c5c883f1b875.nap
            :param outpath:  The local path in which to store .nap files
            
        """
        
        infile = open(os.path.normpath(linkfile), "r")

        for line in infile:
                print line
                req = urllib2.Request(line)  
                try: 
                    f = urllib2.urlopen(req,timeout=500)
                    data = f.read()
   
                    napfile = open(os.path.normpath('%s/%s' % (outpath,filename), "w"))
                    napfile.write(data)
                    napfile.close()
                except urllib2.HTTPError as h:
                    print h   
                except socket.timeout as s:
                    print s   
                           
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

def mungeDatasets(self):
    
    with open('/Users/peder/dev/goc/nrcan.links', 'r') as inF:
        for line in inF:
            fr, en = str(line).strip().split(", ")
    self.out.close()  

if __name__ == "__main__":


    gather_products()    
