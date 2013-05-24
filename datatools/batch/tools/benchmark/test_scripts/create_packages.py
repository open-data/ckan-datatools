import random
import time
import urllib2
import uuid
import json


class Transaction(object):
    def __init__(self):
        self.custom_timers = {}
        
    def run(self):
        name = uuid.uuid1()
        keywords = []
        payload=json.dumps({'name':str(name),'tags':[{'name':'tennis','name':'test'}],"resources":[{"name":"resource"+str(name),"url":"http://www.tennis.com/"+str(name)}]}) 
        header = {'Authorization':'tester','Content-Type': 'application/json'}
        req = urllib2.Request('http://localhost:5000/api/action/package_create', payload,header)

        start_timer = time.time()       
        resp = urllib2.urlopen(req)
        content = resp.read()
        latency = time.time() - start_timer    
        self.custom_timers['Example_Homepage'] = latency
        assert (resp.code == 200), 'Bad HTTP Response'
        #assert ('Welcome to CKAN' in content), 'Failed Content Verification'
 
if __name__ == '__main__':
    trans = Transaction()
    trans.run()
    print trans.custom_timers

