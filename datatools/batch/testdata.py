import os
import time

def create():
    """
        Creates 25 records from each data source to copied to CKAN extension
        
    """
    # Find the latest nrcan .jl file and grab 25 records at random
    
    # Find the lastest Pilot .jl file and grab 25 records at random
    basepath = '/Users/peder/dev/goc/LOAD'
    for  (path, dirs, files) in os.walk(os.path.normpath(basepath)):

        for name in files:
            print 
            print os.path.getmtime(os.path.join(path, name))
            
        

if __name__ == "__main__":
    create()