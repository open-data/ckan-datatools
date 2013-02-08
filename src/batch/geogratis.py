# Inspired by https://github.com/okfn/ckanext-pdeu/blob/master/ckanext/pdeu/harvesters/digitaliser_dk.py

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

    
if __name__ == "__main__":

    file = open('/Users/peder/temp/nrcantest.txt','w')
    file.write("[")
    gather_stage()
    file.write("]")
