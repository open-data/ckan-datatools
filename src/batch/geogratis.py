# Inspired by https://github.com/okfn/ckanext-pdeu/blob/master/ckanext/pdeu/harvesters/digitaliser_dk.py

from lxml import etree
import urllib2
import os
import json
from pprint import pprint
import ckan_api_client
import sys
from pprint import pprint

NEXT = "http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/?alt=json&max-results=50"


def gather_stage():
    global NEXT
    data = []
    while True:
        req = urllib2.Request(NEXT)
        print req.get_full_url()

        response = urllib2.urlopen(req)
#        print response
#        sys.exit()
        opener = urllib2.build_opener()
        f = opener.open(req)
        json_response = json.loads(str(f.read()),"utf-8")
        
        # Get the link to the next batch of links
        links = json_response['links']
        for  link in links:
            if link['rel']=='next': 
                NEXT = link['href'] 
                break
        
        ckan={}
        for product in json_response['products']:
       
            data.append({'id':product['id'],'title':product['title']})
        
        pprint(data)
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
    gather_stage()
