from ckanext.canada.metadata_schema import schema_description as schema
from pprint import pprint
from lxml import etree
from collections import namedtuple


class ResourceDict:
    ''' this is cool but useless ?  '''
    def __init__(self,fields):      
        print fields
        self.__dict__.update(fields)

class FieldMap:
    def __init__(self,name):
        pass
class Resource:
    name=None
    name_fra=None
    url=None
    resource_type=None
    format=None
    
class RawPilotResource(Resource):
    # collect values from xml and map them to field names
    def __init__(self,node):
        
        self.url = node.find()
    
    


'''       
    def validate(self):
        pass
    
    def json(self):
        pass
    
    def diplay(self):
        print url
        
    @staticmethod  
    def required_fields():
        print "WE ARE REQUIRED"
        pprint([(n,l,f['id']) for n,l,f in schema.resource_field_iter()])
           
            
        
        #print[field for field in fields if field
'''
class BasePackage:
    id="1234"
    resources=[]
    
    def __init__(self,id,name,resources, **kwargs):
        super().__init__(**kwargs)
        self.id=id
        self.name=name
        self.resources=resources
    def validate(self):
        pass
    
    def json(self):
        pass
    
    def display(self):
        print "DATASET DETAILS"
        print self.id
        print self.name
        print self.resources
        print "RESOURCES"
        for resource in resources:
            resource.display()
    
class NrcanPackage(BasePackage):
    def __init__(self,id,map,**kwargs):
        super(NrcanPackage,self).__init__(id,'name',['a','b'],**kwargs)
        self.map = map
        
    def display(self):
        super().display()
        
        
class PilotPackage(BasePackage):
    pass


       
if __name__ == "__main__":

    import socket       
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 2401))
    print("Received: {0}".format(client.recv(1024)))
    client.close()
    
    
    
    ''''
    resource_fields = ((n,'') for n,l,f in schema.resource_field_iter())
    #for ckan_name, pilot_name, field in schema_description.dataset_all_fields():
    fields = [(ckan_name,pilot_name) for ckan_name,pilot_name,field in schema.resource_all_fields()]
    pprint(fields)
    print resource_fields
    d = ResourceDict(dict(resource_fields))
    print dir(d)
    print d.name
    d.name="FOOOOOO"
    d.fim = 'fim'
    print d.fim
    print d.name
    
    #print dir(p)
    #BaseResource.required_fields()
    
    
    def doit(foo,faa):
        print foo,faa
    
    print mydict
    
    doit(**mydict)
    '''
        
    
        