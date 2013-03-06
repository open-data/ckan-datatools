#!/usr/bin/python

import sys, getopt
from optparse import OptionParser
import setup_data
import urllib2
import json
from pprint import pprint 
import argparse
from ConfigParser import SafeConfigParser 
from sqlalchemy import *
from datetime import datetime
from ckanext.canada.metadata_schema import schema_description
from jsonpath import jsonpath
import socket 

class Package:
    ''' Takes json from any GOC source and maps it to CKAN 2.0 'package' field values, including extras  '''
    pass
class Resourse:
    ''' Takes json from any GOC source and maps it to CKAN 2.0 'resource' field values, including extras  '''
    pass

class DataManager:
    server = 'http://localhost:5000'
    apikey = 'tester'
    debug_proxy = 'http://localhost:8888'
    
    def __init__(self, server):
        self.server = server
        self.api_base = "/api/action/"
        self.port = 5000
        self.debug_proxy = 'http://localhost:8888'
        self.url =  self.server + self.api_base
        
    def test(self):
        ''' Creates a test package in CKAN, retrieves it to verify that it was entered, and then deletes it '''
        test_package = {'name':'delete-me-package','title':'Test Package Title'}
        response = self.api3_call('package_create',test_package)

        #this is a bit confusing: you can pass the 'name' to 'id' to delete the package
        delete_package = {'id':'delete-me-package'}
        response = self.api3_call('package_delete',delete_package)
      
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

    def delete_by_owner(self,org):
      for item in self._packages(org):
            self.api3_call('package_delete', {'id':item})
   
    def pre_populate(self):
        ''' delegation method  '''
        self.create_organizations()
   
    def create_organizations(self):
        ''' Create Government Organizations in CKAN '''
        for d in setup_data.departments:
            organization = {'name':d['name'],'title':d['title'], 'description':d['description']}
            self.api3_call('organization_create',organization)
    
    def api3_call(self,call,payload): 
       ''' To use a proxy for debugging JSON,  set it here  '''
       proxy_handler = urllib2.ProxyHandler({'http': self.debug_proxy})
       #An undocument trick is to create an empty proxy handler to force urllib2 not to use a proxy
       #proxy_handler = urllib2.ProxyHandler({})
       opener = urllib2.build_opener(proxy_handler)
       #proxy = urllib2.ProxyHandler({'http': 'http://jakoped:L00p2oo1@stcweb.statcan.ca:80'})
       proxy = urllib2.ProxyHandler({'http': 'http://localhost:8888'})
       auth = urllib2.HTTPBasicAuthHandler()
       #opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
       urllib2.install_opener(opener)
       url = self.url+call 
       header = {'Authorization':self.apikey,'Content-Type': 'application/json'}
       data=json.dumps(payload)
       print url
       req = urllib2.Request(url, data, header)
       try:
           r = opener.open(req)
           result = json.loads(r.read())
           if result['success']: 
               return result
           elif result['false']:
               print "*******  API ERROR  ********"
               print result
               
       except urllib2.HTTPError as h:
           print "some Error "
           print h

class Munge:
    pass

class NrcanMunge(Munge):
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
        
    def save_nrcan_data(self):
        ''' Grab NRCan Data and dump into a file '''

        opener = urllib2.build_opener()
        infile = open('/Users/peder/dev/goc/nrcan.links', "r")
        outfile = open('/Users/peder/dev/goc/nrcan.dat', "w")
        for line in infile:
            en, fr = str(line).strip().split(', ')
            req = urllib2.Request(en)  
            try: 
                f = opener.open(req,timeout=500)
            except socket.timeout:
                print "en socket timeout"
            response = f.read() 
            data_en = json.loads(response)
            req = urllib2.Request(fr)  
            try: 
                f = opener.open(req,timeout=500)
            except socket.timeout:
                print "fr socket timeout"
            response = f.read() 
            data_fr = json.loads(response)
            outfile.write(str(data_en) + "|" + str(data_fr) + "\n")
            pass
        
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

class Package:
    pass
class Resource:
    pass
    

        
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
            

class NrcanDb:
  
    db = create_engine('sqlite:///nrcan.db')
    metadata = MetaData(db)
    
    def __init__(self):
        pass
    
    
    def setup(self): 
        ''' A list of products was originally created by running queries in geogratis.py to create 171,909 links to metadata 
            The french list of products has 171,920 and so is out of sync
        '''
        product_links_en = Table('products_links_en', metadata,
                Column('id', Integer, primary_key=True),
                Column('uuid', String(40)),
                Column('link', String),
                Column('json', String),
        )
        #product_links_en.create()  
        
        nrcan_en = Table('nrcan_en', metadata,
                Column('id', Integer, primary_key=True),
                Column('uuid', String(40)),
                Column('time', DateTime),
                Column('json', String),
        )
        nrcan_en.create()  
    
        nrcan_fr = Table('nrcan_en', metadata,
                Column('id', Integer, primary_key=True),
                Column('uuid', String(40)),
                Column('time', DateTime),
                Column('json', String),
                Column('en_id', String),
        )
        nrcan_en.create()  
        pass

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
        '''
        # Most WHERE clauses can be constructed via normal comparisons
        s = users.select(users.c.name == 'John')
        run(s)
        s = users.select(users.c.age < 40)
        run(s)
        
        i = self.nrcan_en.insert()
        i.execute({'uuid': '3036639a-3cae-5bd0-bcd2-8e62a1b7bc51', 'time': datetime.now(), 'json': '{somejason}'})  
        s = self.nrcan_en.select()
        rs = s.execute()
    
        row = rs.fetchone()
        print 'Id:', row[0]
        print 'uuid:', row['uuid']
        print 'Time:', row.time
        print 'json:', row['json']
        
        for row in rs:
            print row.uuid, 'has json', row.json
        '''   
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
         
        
if __name__ == "__main__":
    main_parser = argparse.ArgumentParser(add_help=False)
    main_parser.add_argument("-v", "--verbose", help="increase output verbosity", action='store_true')
    ckan_parser = argparse.ArgumentParser(parents=[main_parser])
    ckan_parser.add_argument('endpoint', help='The data you wish to operate on', action='store',choices=['ckan','pilot','nrcan'])
    ckan_parser.add_argument('action', help='The Action you wish to perform on the data', action='store',choices=['init','list','update','report'])
    ckan_parser.add_argument('entity', help='The data entity you wish to operate on', action='store',choices=['org','group','user','pack'])
    ckan_parser.add_argument("-s","--server", help="CKAN Server.  Default is localhost:5000", action='store', default="localhost:5000")
    ckan_parser.add_argument("-p","--proxy", help="Proxy for debugging etc. Default is None", action='store', default=None,)
    ckan_parser.add_argument("-k","--apikey", help="API Key. Default is tester", action='store', default="tester",)
   
    args = ckan_parser.parse_args()
 
    DataManager.server = args.server
    DataManager.proxy = args.proxy
    DataManager.apikey = args.apikey


    if args.endpoint == 'nrcan':
        if args.action == 'init':
            NrcanMunge().save_nrcan_data()
            #FieldMapper().makeConfig();
            #NrcanMunge().create_ckan_data();
            #NrcanDb().test()
        elif args.action == 'update':
            NrcanReport().createJsonBulkData()
    if args.action == 'list':
        DataManager(args.server).list_by_organization(args.organization)
    elif args.action == 'init' and args.entity == 'orgs':
        DataManager(args.server).create_organizations()
    elif args.action == 'delete':
        DataManager(args.server).delete_by_owner(args.organization)
        
   
