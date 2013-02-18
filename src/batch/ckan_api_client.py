import json
import requests
import os
import urllib2


def api3_call(payload):
   # An undocument trick is to create an empty proxy handler to force urllib2 not to use a proxy
   proxy_handler = urllib2.ProxyHandler({})
   opener = urllib2.build_opener(proxy_handler)
   req = urllib2.Request('http://localhost:5000/dataset')
   r = opener.open(req)
   result = r.read()
   print result
   pprint(json.dumps(payload))
   proxy = {
       "http:":"http://jakoped:L00p2oo1@stcweb.statcan.ca:80",
       "https:":"http://jakoped:L00p2oo1@stcweb.statcan.ca:80"
   }
   headers = {'Authorization': 'tester'}
   url = u"http://127.0.0.1:5000/api/action/package_create"
   #payload = {'name': 'myoooonamyowauire'}
   headers = {'Authorization': 'tester','content-type': 'application/json'}
   r = requests.post(url, data=json.dumps(payload), headers=headers)
   print r.status_code

def submit(package, entity='dataset'):
    body = json.dumps(package)
    headers = {'Authorization': 'tester','Content-type': 'application/json', 'Accept': 'text/plain'}
    #url = u"http://localhost:5000/api/rest/" + entity   
    url = "http://f7odweba1/data/api/rest/" + entity
    proxy = {
        "http:": "%s"  % os.environ['HTTP_PROXY'], 
        "https:": "%s"  % os.environ['HTTP_PROXY']
    }   
    
    '''
        You may need to set a proxy with:
   

        
        r = requests.post(url=url, data=body, headers=headers,proxies=proxy)
        
        Can also pick it up from the config file.  Python requests library appears to have a bug 
        reuiring proxy protocols to have a colon in it: "http:" -  that is not the name of a protocal, 
        and mismatched the documentation
    
    '''

    r = requests.post(url=url, data=body, headers=headers)
    print "-----------------"
    print r.request
    #print r.content
    print r.status_code


def update(struct, name, entity='dataset'):
    body = json.dumps(struct)
    headers = {'Authorization': 'tester','Content-type': 'application/json', 'Accept': 'text/plain'}
    #url = u"http://localhost:5000/api/rest/" + entity   
    url = "http://f7odweba1/data/api/rest/%s/%s" % (entity,str(name))
    print "-----" + url
    proxy = {
            "http:": "%s"  % os.environ['HTTP_PROXY'], 
            "https:": "%s"  % os.environ['HTTP_PROXY']
        }     
    r = requests.post(url=url, data=body, headers=headers,proxies=proxy)
  
    print r.headers
    print r.status_code

def insert(struct, entity='dataset'):
    #that's a messed up bug! Double colons: https://github.com/kennethreitz/requests/issues/688
    headers = {'Authorization': 'tester','Content-type': 'application/json', 'Accept': 'text/plain'}
    body = json.dumps(struct,sort_keys=True)
    url = u"http://localhost:5000/api/rest/package" #+entity
    #print body
    '''
    proxy = {
                "http:": "%s"  % os.environ['HTTP_PROXY'], 
                "https:": "%s"  % os.environ['HTTP_PROXY']
            }   
    '''  
    r = requests.post(url=url, data=body, headers=headers)
    print r.url
    
    #print r.headers
    print r.status_code
