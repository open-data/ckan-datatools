# Inspired by https://github.com/okfn/ckanext-pdeu/blob/master/ckanext/pdeu/harvesters/digitaliser_dk.py

''' This module is used to read data from the Geogratis web services into two master data files, 
    one in english and one in french.
    Then tools are provided to generate reports on the data and import it into CKAN  etc. '''

from lxml import etree
import urllib2
import os
import json
from pprint import pprint
import ckan_api_client
import sys
from pprint import pprint
import time
import socket 
import requests
from itertools import *
        
NEXT = "http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/?alt=json&max-results=50"
LAST_REQUEST =''
def gather_stage():
    global total_download
    global LAST_REQUEST
    global NEXT
    #if LAST!='':NEXT="http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/?alt=json&max-results=50&start-index=%s" % LAST_REQUEST

    total_download = 0

    data = []
    opener = urllib2.build_opener()
    while True:
        
        #Content-Length is optional; use it if it's present, to cut down on bandwidth use,
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
            #pprint(product)
        '''
            # get the number 
            Do something with products here 
            #ckan['name'] = '003nrcan-%s' % product['id'].split('-')[0]
            ckan['name'] = "package-with-extras-in-resource"
            ckan['title'] = product['title']
            ckan['groups'] =  ['nrcan']
            resources=[]
            for link in product['links']:
                if link['rel'] == 'alternate':
                    try: resources.append({'url':link['href'],'format':link['enctype'].split('/')[1]})
                    except KeyError: pass
            ckan['resources'] = resources
            ckan_api_client.insert(ckan)
            sys.exit()
            pass
        return False
   
        for handle in doc.findall(self.NS + "ResourceHandle"):
            link = handle.get('handleReference')
            id = sha1(link).hexdigest()
            obj = HarvestObject(guid=id, job=harvest_job, content=link)
            obj.save()
            ids.append(obj.id)
        firstResult += maxResults
        if firstResult > int(doc.getroot().get('totalResults')):
            break
    return ids
    '''
    pass
def test_single():   
    json_data=open('data/nrcan-single.json')
    data=json.load(json_data)
    create_package(data)
    
def create_package(data):
    #package_dict = {'extras':{},'resources':[],'tags':[]}
    package_dict={}
    package_dict['author'] = data['author']
    package_dict['author_email'] = 'geoginfo@NRCan.gc.ca'
    #package_dict['id'] = data['id']
    package_dict['maintainer_email'] = 'geoginfo@NRCan.gc.ca'
    package_dict['name'] = "somename2" #data['id']
    package_dict['notes'] = data['summary']
    '''
    package_dict['organization'] = 'Natural Resources Canada'
 
    package_dict['owner_org'] = 'nrcan'

    package_dict['title'] = data['title']
    package_dict['url'] = 'http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/' + data['id'] + '.html'
    #Array fields
    package_dict['extras'] = []
    package_dict['groups'] = ['nrcan']
    package_dict['resources'] = []
    package_dict['tags'] = []
    
    '''
    api_call(package_dict)
    #ckan_api_client.insert(package_dict)
    pass

def api_call(payload):
    pprint(json.dumps(payload))
    headers = {'Authorization': 'tester'}
    url = u"http://localhost:8080/api/action/package_create"
    #payload = {'name': 'myoooonamyowauire'}
    headers = {'Authorization': 'tester','content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    print r.status_code
    
def report(fname1,fname2,outfile):
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
     
if __name__ == "__main__":
    report("/Users/peder/dev/goc/nrcan.jl","/Users/peder/dev/goc/nrcan2-fr.jl","/Users/peder/dev/goc/nrcan-combined.txt")
    #test_single()

