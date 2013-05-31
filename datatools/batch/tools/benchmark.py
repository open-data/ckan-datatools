import urllib2

def create_test_data():
    apikey = 'tester'
    url = "http://localhost:5000/api/action/pakcage_create" 
    # create empty proxy handler to bypass statcan proxy
    proxy_handler = urllib2.ProxyHandler({}) 
    header = {'Authorization':apikey,'Content-Type': 'application/json'}
    
    longest = None
    shortest = None
    average  = None   
    i = 0
    while i < 200000:
        name = "testdata"+str(i)
        data=json.dumps({'name':name})
        req = urllib2.Request(url, data, header)
        


if __name__ == "__main__" :
    create_test_data()