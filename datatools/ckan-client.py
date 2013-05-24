import json
import urllib2
    
    
def api3_call(self,call,payload): 
       ''' To use a proxy for debugging JSON,  set it here
       
           NOTE: Create an empty proxy handler to force urllib2 not to use a proxy
           proxy_handler = urllib2.ProxyHandler({})
           
           
           You may need to set a proxy with:
           r = requests.post(url=url, data=body, headers=headers,proxies=proxy)
           
           Examples:
           
           On statcan network B:
           urllib2.ProxyHandler({'http': 'http://jakoped:mypass@stcweb.statcan.ca:80'})
           
           NOTE: Create an empty proxy handler to force urllib2 not to use a proxy if you are 
           entering datasets in localhost on Statcan network B
           proxy_handler = urllib2.ProxyHandler({})
           opener = urllib2.build_opener(proxy_handler)
           
           When using a debugging proxy like Charles to monitor JSON, you can set it with 
           proxy_handler = urllib2.ProxyHandler({'http': 'http://localhost:8888'})
           
           
           NOTE: You may also be able to pick up proxy information from you environment like:
           
            proxy = {
                "http:": "%s"  % os.environ['HTTP_PROXY'], 
                "https:": "%s"  % os.environ['HTTP_PROXY']
            }   
            
        '''
       proxy_handler = urllib2.ProxyHandler({'http': self.debug_proxy})
       
       opener = urllib2.build_opener(proxy_handler)
       #proxy = 
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


    

