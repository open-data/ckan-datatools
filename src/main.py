#!/usr/bin/python

import sys, getopt
from optparse import OptionParser
import setup_data
import urllib2
import json
from pprint import pprint 

class DataImport:
    protocol = 'http://'
    def __init__(self,top_domain):
        self.top_domain = top_domain
        self.api_call = "/api/action/"
        self.port = 5000
        self.url =  self.protocol + self.top_domain + self.api_call
        pass

    def pre_populate(self):
        ''' delegation method  '''
        self.create_organizations()

    def create_organizations(self):
        ''' Create Government Organizations in CKAN '''
        print "creating organizations for " + self.top_domain
        for d in setup_data.departments:
            organization = {'name':d['name'],'title':d['title'], 'description':d['description']}
            self.api3_call('organization_create',organization)
            
            
     
    def api3_call(self,call,payload): 
       #An undocument trick is to create an empty proxy handler to force urllib2 not to use a proxy  
       proxy_handler = urllib2.ProxyHandler({})
       opener = urllib2.build_opener(proxy_handler)
       url = self.url+call 
       print url
       header = {'Authorization':'tester','Content-Type': 'application/json'}
       data=json.dumps(payload)
       print data
       req = urllib2.Request(url, data, header)
       try:
           r = opener.open(req)
           result = r.read()
           pprint(result)
       except urllib2.HTTPError as h:
           print "some Error "
           print h



def cli(argv):
    try:
        opts, args = getopt.getopt(argv, "hi:o", ["munge=","server="])
        DataImport(argv[1:0]).pre_populate()
    except getopt.GetoptError:
        print 'munge.py -m <test|all> -c <ckan> -p <proxy>'
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print 'munge.py -m <test|all> -c <ckan> -p <proxy>'

if __name__ == "__main__":   

	DataImport(*sys.argv[1:2]).pre_populate()