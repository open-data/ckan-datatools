'''
Created on 2013-01-10

@author: jakoped

Extracting field mappings by scraping 
government websites for government department acronyms etc.

'''


def departments():
    '''
    Extract department information from  
    http://www.canada.gc.ca/depts/major/depind-eng.html
    using //*[@id="cn-centre-col-inner"]/section[$a-b]/ul/li[$get_all]/a
  '''