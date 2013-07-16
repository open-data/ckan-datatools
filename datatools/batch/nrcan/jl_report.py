#-*- coding:UTF-8 -*-
import sys
import json
from collections import Counter
from pprint import pprint

def  resource_formats(file):

    lines = [line.strip() for line in open(file)]
    for  i,line in enumerate(lines):
        package = json.loads(line)
        for resource in package['resources']:
            try: 
                if resource['size']:
                    print "-------"
                    print resource['format']
                    print resource['url']
            except:
                pass
        


if __name__ == "__main__":
    
    load_dir = '/Users/peder/dev/goc/LOAD'
    jl_file= load_dir + "/nrcan-full-2013-06-10.jl"
    resource_formats(jl_file)
    