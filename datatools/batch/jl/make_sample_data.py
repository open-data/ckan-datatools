'''
Create sample.jl file from 25 random datasets 
from each .jl file (pilot and nrcan) and place 
it in source/ckanext-canada/data/sample.jl

It should be run just after new datafiles have been produced

'''

if __name__ == "__main__":
    
    basedir = '/Users/peder/dev/goc/LOAD'
    pilot_file =  "{}/pilot-{}.jl".format(outputdir,date.today()) 
    nrcan_file =  "{}/nrcan-{}.jl".format(outputdir,date.today())
    