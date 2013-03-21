'''
Created on Jan 9, 2013

@author: peder
'''

from collections import namedtuple

Pack = namedtuple("Pack", "name title genre", True, True)
test_data = [
        Pack("Pratchett", "Nightwatch", "fantasy"),
        Pack("Pratchett", "Thief Of Time", "fantasy"),
        Pack("Le Guin", "The Dispossessed", "scifi"),
        Pack("Le Guin", "A Wizard Of Earthsea", "fantasy"),
        Pack("Turner", "The Thief", "fantasy"),
        Pack("Phillips", "Preston Diamond", "western"),
        Pack("Phillips", "Twice Upon A Time", "scifi"),
        ]

def stuff():
    ''' 
    Really simple list comprehension example:
    '''

    word = "Hello"
#    new = {item: word.count(item) for item in set(word)}
#    print new
    
    def foo(w): 
        return "Becomes " + w + "o" 
      
    new = {item: foo(item) for item in set(word)}
    print new

    '''
    That set comprehension sure is short in comparison to the set up required! If we'd 
    used a list comprehension, of course, Terry Pratchett would have been listed twice. 
    As it is, the nature of sets removes the duplicates and we end up with:
    '''
    
    test_data1 = { b.name for b in test_data if b.genre == 'fantasy' }

    print test_data1
    
    test_data_double = [ b.name for b in test_data if b.genre == 'fantasy' ]
     
    print test_data_double
    
    """
    We can introduce a colon to create a dictionary comprehension. This converts a 
    sequence into a dictionary using key : value pairs. For example, it may be useful to 
    quickly look up the author or genre in a dictionary if we know the title. We can use a 
    dictionary comprehension to map titles to book objects:
    
    """
    test_data_lookup = { b.name: b.name for b in test_data if b.genre == 'fantasy' }
    
    print test_data_lookup
    
    ''' Now do the same with (), and it becomes a generator without creating a new object in memory '''
    
    test_data_generator = (b.name for b in test_data if b.genre == 'fantasy' )
    for l in test_data_generator:
            print l
            
    '''  OK, lets use a yield to return an object.  When Python sees yield in a 
function, it takes that function and wraps it up in an object '''
        
    def foo_filter(insequence):
        for l in insequence:
            if 'fantasy' in l:
                yield l
            else:
                yield l
                
    filter = foo_filter(test_data)
    for l in filter:
        print l
    
    pass   

class Options:
    default_options = {
            'port': 21,
            'host': 'localhost',
            'username': None,
            'password': None,
            'debug': False,
            }
    def __init__(self, **kwargs):
        self.options = dict(Options.default_options)
        self.options.update(kwargs)
    def __getitem__(self, key):
        return self.options[key] 

if __name__ == '__main__':
    def default_arguments(x, y, z, a="Some String", b=False):
        pass
    #kwargs("a string", 2, 14, b=True)
    
    options = Options(username="dusty", password="drowssap",debug=True)
    print options['debug']
    
    for t in test_data:
        print t
        print t.__repr__()
 