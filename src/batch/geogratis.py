# Inspired by https://github.com/okfn/ckanext-pdeu/blob/master/ckanext/pdeu/harvesters/digitaliser_dk.py

from lxml import etree
import urllib2
import os
import json
from pprint import pprint
import ckan_api_client
import sys
from pprint import pprint

API_ENDPOINT = "http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/"
JSON_CALL = "ess-sst?max-results=100"
#?start-index=934355&max-results=100
def make_request(url):
    print url
    
#    proxy = {
#        "http:": "%s"  % os.environ['HTTP_PROXY'], 
#        "https:": "%s"  % os.environ['HTTP_PROXY']
#    }   
    

    r = requests.get(url=url)
    return r.json

def add_extras_to_package():
    #try: resources.append({'foo':'my-foo-variable','url':link['href'],'format':link['enctype'].split('/')[1]})                 
    pass

def add_extras_to_resources():
    pass

def gather_stage(harvest_job):
    
    startIndex = ''
    maxResults = 5
    firstCall = "http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/?alt=json"
    ids = []
    next=''
    while True:
        #req=firstCall
        req='http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/?start-index=934355&max-results=100&alt=atom'
        #req = API_ENDPOINT +  '?start-index=%s&max-results=%s&alt=json' % (startIndex,maxResults)
        print req
        response = urllib2.urlopen(req)
        opener = urllib2.build_opener()
        f = opener.open(req)
        #print f.read()
        
        #json_response = json.loads(str(opener.open(req).read()),"utf-8")
        #simplejson.load(f)
        json_response = json.loads(str(f.read()),"utf-8")
        links = json_response['links']
        print links
        print "goodbye"
        sys.exit()
        key = [i for key,value in links.items if value=='next' ][0]
        print key
        if any(l['rel'] == 'next' for l in links):
            print "yep"
            next = l['href']
       
        print next

        #pprint(next)
       
        ckan={}
        for product in json_response.json['products']:
            
            print product['parameters']
            # get the number 
            '''
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

    
if __name__ == "__main__":
    gather_stage(API_ENDPOINT)
