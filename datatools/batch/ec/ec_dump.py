import os
import sys
from lxml import etree
from pprint import pprint
import json
from datetime import date
from datatools.batch.nrcan import nrcan_dump as nrcan_dump

def process(dir,outfile): 
    counter=0

    jlfile = open(os.path.normpath(outfile), "w")
    for (path, dirs, files) in os.walk(os.path.normpath(dir)):
        for n,file in enumerate(files):
            if file =='metadata.iso19139.xml':
                counter+=1
                f = open(os.path.join(path,file),"r")
                doc = etree.parse(f)
                nrcan_dump.doc = doc
                nrcan_dump.data_identification()
                
                nrcan_dump.time_and_space()
                
                nrcan_dump.bilingual()
                
                try:
                    nrcan_dump.resources()
                    
                except:
                    print counter,"DID IT BUBBLE?", nrcan_dump.package_dict['id']

                print counter, nrcan_dump.package_dict['title']
                #nrcan_dump.check_structure(nrcan_dump.package_dict)
            #pprint(json.dumps(nrcan_dump.package_dict))
            
            if n>10: sys.exit()
            #print package_dict['id']
            jlfile.write(json.dumps(nrcan_dump.package_dict) + "\n")  
            


if __name__ == "__main__":
    
    outfile ="/Users/peder/dev/OpenData/combined_loads/{}/{}".format(date.today(),"ec.jl")
    dir="/Users/peder/dev/OpenData/data_sources/ec/"

    process(dir,outfile)