#!/usr/bin/python

import sys, getopt
from optparse import OptionParser
import setup_data
import urllib2
import json
from pprint import pprint 

class Package:
    ''' Takes json from any GOC source and maps it to CKAN 2.0 'package' field values, including extras  '''
    pass
class Resourse:
    ''' Takes json from any GOC source and maps it to CKAN 2.0 'resource' field values, including extras  '''
    pass

class DataImport:
    protocol = 'http://'
    def __init__(self,top_domain):
        self.top_domain = top_domain
        self.api_call = "/api/action/"
        self.port = 5000
        self.url =  self.protocol + self.top_domain + self.api_call
        pass
    def test(self):
        ''' Creates a test package in CKAN, retrieves it to verify that it was entered, and then deletes it '''
        test_package = {'name':'delete-me-package','title':'Test Package Title'}
        response = self.api3_call('package_create',test_package)
        print response
        #this is a bit confusing: you can pass the 'name' to 'id' to delete the package
        delete_package = {'id':'delete-me-package'}
        response = self.api3_call('package_delete',delete_package)
        print response

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
       # If you are using a proxy for debugging JSON, you can set it here
       proxy_handler = urllib2.ProxyHandler({'http': 'localhost:8888'})
       #An undocument trick is to create an empty proxy handler to force urllib2 not to use a proxy
       #proxy_handler = urllib2.ProxyHandler({})
       opener = urllib2.build_opener(proxy_handler)
       url = self.url+call 
       print url
       header = {'Authorization':'tester','Content-Type': 'application/json'}
       data=json.dumps(payload)
       req = urllib2.Request(url, data, header)
       try:
           r = opener.open(req)
           result = json.loads(r.read())
           if result['success']: return result['id']
       except urllib2.HTTPError as h:
           print "some Error "
           print h

def cli(argv):
    ''' Command line interface entry point '''
    help = '-c <command[test|load]>  -s <server:port> -p <proxy>'
    try:
        opts, args = getopt.getopt(argv, "hc:s:p", ["server=","proxy="])
        print opts, args
    except getopt.GetoptError as err:
        print str(err) 
        print help
        ''' Unix programs generally use 2 for command line syntax errors '''
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print help
        elif opt == '-c':
             if arg == 'test':
                 print 'Creating single test record '
                 DataImport(arg).test()

        elif opt == 'data':
             print 'trying data import with ' + arg
             DataImport(arg).pre_populate()
            

if __name__ == "__main__": 
    #cli(sys.argv[1:]) 
    DataImport('localhost:5000').test()
