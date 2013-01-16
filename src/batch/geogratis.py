# Inspired by https://github.com/okfn/ckanext-pdeu/blob/master/ckanext/pdeu/harvesters/digitaliser_dk.py

from lxml import etree
import requests
import os
import json
from pprint import pprint
import ckan_api_client

API_ENDPOINT = "http://geogratis.gc.ca/api/en/nrcan-rncan/"
JSON_CALL = "ess-sst?max-results=40&q=islands&alt=json"



def make_request(url):
    print url
    
#    proxy = {
#        "http:": "%s"  % os.environ['HTTP_PROXY'], 
#        "https:": "%s"  % os.environ['HTTP_PROXY']
#    }   
    

    r = requests.get(url=url)
    return r.json
    

def gather_stage(harvest_job):
    
    firstResult = 0
    maxResults = 80

    ids = []
    while True:
        req = API_ENDPOINT +  'ess-sst?max-results=%s&q=islands&alt=json' % (maxResults)
        rep = requests.get(req)
        ckan={}
        for product in rep.json['products']:
            ''' Do something with products here '''
            ckan['name'] = 'nrcan-%s' % product['id'].split('-')[0]
            ckan['title'] = product['title']
            resources=[]
            for link in product['links']:
                if link['rel'] == 'alternate':
                    try: resources.append({'url':link['href'],'format':link['enctype'].split('/')[1]})
                    except KeyError: pass
            ckan['resources'] = resources
            

            ckan_api_client.insert(ckan)
            pass
        return False
        '''
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


def fetch_stage(self, harvest_object):
        doc = etree.parse(harvest_object.content)
        category = doc.findtext('//' + self.NS + 'ResourceCategoryHandle/' + self.NS + 'TitleText')
        if category != "Datakilde":
            return
        package_dict = {'extras': {}, 'resources': [], 'tags': []}
        package_dict['title'] = doc.findtext(self.NS + 'TitleText')
        package_dict['notes'] = doc.findtext(self.NS + 'BodyText')
        package_dict['author'] = doc.findtext(self.NS + \
                'ResourceOwnerGroupHandle/' + self.NS + 'TitleText')
        package_dict['extras']['harvest_dataset_url'] = harvest_object.content

        package_dict['metadata_created'] = doc.findtext(self.NS + 'CreatedDateTime')
        package_dict['metadata_modified'] = doc.find(self.NS + 'PublishedState').get('publishedDateTime')
        
        responsible = doc.findtext(self.NS + 'ResponsibleReference')
        res_doc = etree.parse(responsible)
        package_dict['maintainer'] = res_doc.findtext('//' + self.PSN + 'PersonGivenName') + \
            " " + res_doc.findtext('//' + self.PSN + 'PersonSurnameName')

        package_dict['extras']['categories'] = []
        for tax_handle in doc.findall('//' + self.NS + 'TaxonomyNodeHandle'):
            package_dict['extras']['categories'].append(tax_handle.findtext(self.NS + 'TitleText'))
        
        for tag_handle in doc.findall('//' + self.NS + 'TagHandle'):
            package_dict['tags'].append(tag_handle.findtext(self.NS + 'LabelText'))
        
        ref_handle = doc.find('//' + self.NS + 'ReferenceHandle')
        if ref_handle: 
            ref_doc = etree.parse(ref_handle.get('handleReference'))
            package_dict['url'] = ref_doc.getroot().get('url')

        for artefact in doc.findall('//' + self.NS + 'ArtefactHandle'):
            try:
                art_doc = etree.parse(artefact.get('handleReference'))
                package_dict['resources'].append({
                    'url': art_doc.getroot().get('url'),
                    'format': '',
                    'description': artefact.findtext(self.NS + 'TitleText')
                    })
            except Exception, e:
                log.warn(e)
        
        #from pprint import pprint
        #pprint(package_dict)
        harvest_object.content = json.dumps(package_dict)
        harvest_object.save()
        return True
    
if __name__ == "__main__":
    gather_stage(API_ENDPOINT)
