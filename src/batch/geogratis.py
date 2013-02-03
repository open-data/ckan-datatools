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

NEXT = "http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/?alt=json&max-results=50"

def gather_stage():

    file = open('/Users/peder/temp/nrcantest.txt','w')
    global total_download
    total_download = 0
    global NEXT
    data = []
    opener = urllib2.build_opener()
    while True:
        req = urllib2.Request(NEXT+'&alt=json')
        print req.get_full_url()

        f = opener.open(req)
        response = f.read()
        print len(response)
        total_download += len(response) #To Convert bytes to megabytes: 1048576
        file.write("------------- " + str(total_download) + " ---------------\n")
    
        json_response = json.loads(str(response),"utf-8")
        
        # Get the link to the next batch of links
        links = json_response['links']
        for  link in links:
            if link['rel']=='next': 
                NEXT = link['href'] 
                break

        for product in json_response['products']:     
            #data.append({'id':product['id'],'title':product['title']})  
            file.write("%s    %s\n" % (product['id'],product['title']));  
            
        time.sleep(60)
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
