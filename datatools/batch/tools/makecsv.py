import csv
from collections import OrderedDict
from pprint import pprint
import cStringIO
from pprint import pprint
from ConfigParser import SafeConfigParser   
from collections import OrderedDict 


outfile = '/Users/peder/temp/ckan-dumps/headers.csv'
infile = '/Users/peder/temp/ckan-dumps/dump.csv'

def read_config():
    global config
    config = SafeConfigParser()
    config.read('pilot-batch.config')
    
def write_headers():
    ordered_fieldnames = OrderedDict([('field1',None),('field2',None)])
    with open(outfile,'wb') as fou:
        dw = csv.DictWriter(fou, delimiter='\t', fieldnames=ordered_fieldnames)
        dw.writeheader()
    # continue on to write data

def csv_to_dict():

    data = open().read()
    reader = csv.DictReader(cStringIO.StringIO(data))
    print reader
        
#    for row in reader:
#        print "----"
#        pprint(row) 



def show_headers(file):
    with open(dump) as f:
        reader = csv.reader(open(file))
        for header in reader.next():
            print header
        #print csv.Sniffer().has_header(f.read())
        
def make_headers(file):
    read_config()
    
    ordered_fieldnames = OrderedDict()
    #use this to get a dict
    ordered_fieldnames = config._sections['CKAN-Pilot Fields Mappings']
    # remove __name__
    ordered_fieldnames.pop('__name__')
    print config._sections['CKAN-Pilot Fields Mappings']
    #for f,v in config.items('CKAN-Pilot Fields Mappings'):
       

#    print ordered_fieldnames
    with open(outfile,'wb') as fou:
        dw = csv.DictWriter(fou, delimiter=',', fieldnames=ordered_fieldnames)
        dw.writeheader()


def write_newfile(infile):
    ''' read the headers from a dump file '''
    with open(infile,'rb') as fin, open(outfile,'w+') as fout:  # multiple context expressions
        dr = csv.DictReader(fin, delimiter='\t')
        fieldnames=dr.fieldnames
        dw = csv.DictWriter(fout, delimiter='\t', fieldnames=fieldnames) 
        #dw.writerow(dict((fn,fn) for fn in dr.fieldnames))

if __name__ == "__main__":
    make_headers(outfile)
    #write_newfile(infile)
    
    '''  

        with open(infile,'rb') as fin:
            dr = csv.DictReader(fin, delimiter='\t')
            
        print dr
        
        with open(outfile,'wb') as fou:
            dw = csv.DictWriter(fou, delimiter='\t', fieldnames=dr.fieldnames)
            dw.writerow(dict((fn,fn) for fn in dr.fieldnames))
            for row in dr:
                dw.writerow(row)
                
    '''