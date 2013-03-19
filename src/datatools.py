import sys
import os
import json
import setup_data
import time
import socket 
import urllib2
from jsonpath import jsonpath
from pprint import pprint 
import argparse
from ConfigParser import SafeConfigParser 
from datetime import datetime
from ckanext.canada.metadata_schema import schema_description

class Package:
    ''' Takes json from any GOC source and maps it to CKAN 2.0 'package' field values '''
    pass
class Resourse:
    ''' Takes json from any GOC source and maps it to CKAN 2.0 'resource' field values '''
    pass

class DataManager:
    
    def __init__(self, server,apikey,proxy):
        self.ckan_client = CkanClient(server,apikey,proxy)
        
    def test(self):
        ''' Creates a test package in CKAN, retrieves it to verify that it was entered, and then deletes it '''
        test_package =  eval(open("single.jl", "read").next())
        pprint(test_package)
      
        response = self.ckan_client.api3_call('package_create',test_package)
        #pprint(response)
        #this is a bit confusing: you can pass the 'name' to 'id' to delete the package
#        delete_package = {'id':'delete-me-package'}
#        response = self.api3_call('package_delete',delete_package)
      
    def _packages(self,org): 
        packs = [] 
        if org != 'all':
            response = self.api3_call('package_search',{'q': u'groups: "'+ org + '"'}) 
            for item in response['result']['results']:
                packs.append(item['name'])
        else:
            response = self.api3_call('package_list',{}) 
            for item in response['result']:
                packs.append(item)   
        return packs
                
    def list_by_organization(self,org):
        for item in self._packages(org):
            print item
            
    def set_organizations(self):
        pass

    def delete_by_owner(self,org):
      for item in self._packages(org):
            selfckan_client.api3_call('package_delete', {'id':item})
   
    def pre_populate(self):
        ''' delegation method  '''
        self.create_organizations()
   
    def create_organizations(self):
        ''' Create Government Organizations in CKAN '''
        for data in schema_description.dataset_field_by_id['author']['choices']:
            
            try:
                organization = {'name':str(data['id']).lower(),'title':data['id'], 'description':data['key']}
                organization['id']="sometestid"
                response = self.ckan_client.api3_call('organization_create',organization)
            except KeyError:
                print "MISSING ID or some other key" 
           
            
    def load_data(self,jlfile):
        infile = open(os.path.normpath(jlfile))
        for line in infile:
            response = self.ckan_client.api3_call('package_create',json.loads(line))
            
class FieldMapper:

    schema = schema_description  
    def __init__(self):
        pass
    
    def makeConfig(self):
        ''' When the metadata schema is regenerated, you may have to run this '''
        
        #out = open("nrcan.config", "w")
        out.write('[package]\n')
        fields_fr = []
        for ckan_name,lang, field in self.schema.dataset_fields_by_ckan_id():
            if lang == 'fra':
                fields_fr.append(ckan_name)
            else: 
                out.write(ckan_name +"=\n")

        out.write('\n[package_fr]\n')
        for f in fields_fr:
            out.write(f +"=\n")
                
        out.write('\n[resource]\n')
        fields_fr =[]
        for ckan_name, lang, field in self.schema.resource_fields_by_ckan_id():      
            if lang == 'fra':
                fields_fr.append(ckan_name)
            else: 
                out.write(ckan_name +"=\n")
        out.write('\n[resource_fr]\n')
        for f in fields_fr:
            out.write(f +"=\n")

    def test(self):      
        self.db.echo = True  
        nrcan_en = Table('nrcan_en', self.metadata, autoload=True)
        s = nrcan_en.select()
        rs = s.execute()
        for row in rs:
                print row
        
        def run(stmt):
            rs = stmt.execute()
            for row in rs:
                print row

    def insert_en(self,json):
        self.db.echo = True  
        nrcan_en = Table('nrcan_en', self.metadata, autoload=True)
        i = nrcan_en.insert()       
        i.execute({'uuid': json['id'], 'time': datetime.now(), 'json': json}) 
        
        row = rs.fetchone()
        print row
        
    def insert_fr(self,json):
        self.db.echo = True  
        nrcan_en = Table('nrcan_en', self.metadata, autoload=True)
        i = nrcan_fr.insert()       
        i.execute({'uuid': json['id'], 'time': datetime.now(), 'json': json, 'en_id':1}) 
        
        row = rs.fetchone()
        print row   
        sys.exit(0)  
    def delete(self):
        s = self.nrcan_en.select()
        rs = s.execute()
        row = rs.fetchone()

class CkanClient:
    server = 'http://localhost:5000'
    apikey = 'tester'
    proxy = 'http://localhost:8888'
    
    def __init__(self, server,apikey,proxy='http://localhost:8888'):
        self.server = server
        self.apikey = apikey
        self.proxy = proxy
    
    def api3_call(self,call,payload): 
           ''' 
               You may need to set a proxy with:
               r = requests.post(url=url, data=body, headers=headers,proxies=proxy)
    
               Example:  On statcan network B:
               urllib2.ProxyHandler({'http': 'http://jakoped:mypass@stcweb.statcan.ca:80'})
    
               When using a debugging proxy like Charles to monitor JSON, you can set it with 
               proxy_handler = urllib2.ProxyHandler({'http': 'http://localhost:8888'})
               
                You may also be able to pick up proxy information from you environment like:
               
                proxy = {
                    "http:": "%s"  % os.environ['HTTP_PROXY'], 
                    "https:": "%s"  % os.environ['HTTP_PROXY']
                }  
                
                Urllib2 trick: Create an empty proxy handler to force urllib2 not to use a proxy when 
                testing on localhost on statcan desktops: proxy_handler = urllib2.ProxyHandler({}) 
                
           '''

           print time.time()
           url = self.server + "/api/action/"
           #proxy_handler = urllib2.ProxyHandler({'http': self.debug_proxy})
           #payload = {'name':'testname'}

           
           #proxy_handler = urllib2.ProxyHandler({'http': self.proxy})
           #opener = urllib2.build_opener(proxy_handler)
           #auth = urllib2.HTTPBasicAuthHandler()
           #opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
           #urllib2.install_opener(opener)
           url = url+call 
           header = {'Authorization':self.apikey,'Content-Type': 'application/json'}
           data=json.dumps(payload)
           #print url
           req = urllib2.Request(url, data, header)
           try:
               r = urllib2.urlopen(req)
               
               #r = opener.open(req)
               result = json.loads(r.read())
               if result['success']: 
                   
                   return result
               elif result['false']:
                   print "*******  API ERROR  ********"
                   print result
                   
           except urllib2.HTTPError as h:
               print  h
  
if __name__ == "__main__":
    main_parser = argparse.ArgumentParser(add_help=False)
    main_parser.add_argument("-v", "--verbose", help="increase output verbosity", action='store_true')
    ckan_parser = argparse.ArgumentParser(parents=[main_parser])
    ckan_parser.add_argument('endpoint', help='The data you wish to operate on', action='store',choices=['ckan','pilot','nrcan'])
    ckan_parser.add_argument('action', help='The Action you wish to perform on the data', action='store',choices=['init','load','list','update','report','test'])
    ckan_parser.add_argument('entity', help='The data entity you wish to operate on', action='store',choices=['org','group','user','pack'])
    ckan_parser.add_argument("-s","--server", help="CKAN Server.  Default is localhost:5000", action='store', default="localhost:5000")
    ckan_parser.add_argument("-p","--proxy", help="Proxy for debugging etc. Default is None", action='store', default=None,)
    ckan_parser.add_argument("-k","--apikey", help="API Key. Default is tester", action='store', default="tester",)
    ckan_parser.add_argument("-j","--jsondata", help="Path to .jl CKAN data file", action='store',)
    
    args = ckan_parser.parse_args()
 
    DataManager.server = args.server
    DataManager.proxy = args.proxy
    DataManager.apikey = args.apikey


    if args.endpoint == 'nrcan':
        if args.action == 'init':
            NrcanMunge().save_nrcan_data()
        elif args.action == 'update':
            NrcanReport().createJsonBulkData()
    elif args.endpoint == 'ckan':
        if args.action == 'init' and args.entity == 'org':
            DataManager(args.server,args.apikey,args.proxy).create_organizations()
        elif args.action == 'load' and args.entity == 'pack':
            DataManager(args.server,args.apikey,args.proxy).load_data(args.jsondata)
        elif args.action == 'delete':
            DataManager(args.server).delete_by_owner(args.organization)
        
   
