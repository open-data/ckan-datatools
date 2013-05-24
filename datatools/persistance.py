from sqlalchemy import *

class NrcanDb:
  
    db = create_engine('sqlite:///nrcan.db')
    metadata = MetaData(db)
    
    def __init__(self):
        pass
    
    def setup(self): 
        ''' A list of products was originally created by running queries in geogratis.py to create 171,909 links to metadata 
            The french list of products has 171,920 and so is out of sync
        '''
        product_links_en = Table('products_links_en', metadata,
                Column('id', Integer, primary_key=True),
                Column('uuid', String(40)),
                Column('link', String),
                Column('json', String),
        )
        #product_links_en.create()  
        
        nrcan_en = Table('nrcan_en', metadata,
                Column('id', Integer, primary_key=True),
                Column('uuid', String(40)),
                Column('time', DateTime),
                Column('json', String),
        )
        nrcan_en.create()  
    
        nrcan_fr = Table('nrcan_en', metadata,
                Column('id', Integer, primary_key=True),
                Column('uuid', String(40)),
                Column('time', DateTime),
                Column('json', String),
                Column('en_id', String),
        )
        nrcan_en.create()  
        pass