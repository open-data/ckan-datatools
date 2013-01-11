import json
import requests
import os

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
    print ">>>>>" + body
    print ">>>>>" + str(name)
    url = "http://f7odweba1/data/api/rest/%s/%s" % (entity,str(name))
    print "-----" + url
    proxy = {
            "http:": "%s"  % os.environ['HTTP_PROXY'], 
            "https:": "%s"  % os.environ['HTTP_PROXY']
        }     
    r = requests.post(url=url, data=body, headers=headers,proxies=proxy)
  
    print r.headers
    print r.status_code

def insert(body, entity='dataset'):
    #that's a messed up bug! Double colons: https://github.com/kennethreitz/requests/issues/688
    headers = {'Authorization': 'tester','Content-type': 'application/json', 'Accept': 'text/plain'}
    #body = json.dumps({u"name":"test223332211222211", u"title":"Test datasetddfdsddf 1111"})
    url = u"http://localhost:5000/api/rest/"+entity
    
    proxy = {
                "http:": "%s"  % os.environ['HTTP_PROXY'], 
                "https:": "%s"  % os.environ['HTTP_PROXY']
            }     
    r = requests.post(url=url, data=body, headers=headers,proxy=proxy)
  
    print r.headers
    print r.status_code