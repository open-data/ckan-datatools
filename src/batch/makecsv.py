import csv
from collections import OrderedDict


outfile = '/Users/peder/temp/ckan-dumps/eggs3.csv'
infile = '/Users/peder/temp/ckan-dumps/statcan.csv'

def write_headers():
    ordered_fieldnames = OrderedDict([('field1',None),('field2',None)])
    with open(outfile,'wb') as fou:
        dw = csv.DictWriter(fou, delimiter='\t', fieldnames=ordered_fieldnames)
        dw.writeheader()
    # continue on to write data
 

if __name__ == "__main__":
    
    write_headers()
#    with open('/Users/peder/temp/ckan-dumps/eggs2.csv', 'wb') as csvfile:
#        spamwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
#        spamwriter.writeheader('foo','ffoo','fooa','fooofim','jjjjj')
#        spamwriter.writerow(['Spam'] * 5 + ['Baked Beans'])
#        spamwriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])
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