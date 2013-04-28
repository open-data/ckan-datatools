import sys
import lxml
import common
from collections import Counter
from pilot_model import PilotHoldings, PilotRecord

class PilotDelegator:
    """
        To work with pilot data, its best for first create
        the data in memore for later manipulation rather than reading it 
        again and again from the xml.
        
        When dealing with a collection of records, encapsulation is very useful:
        I only want to know that a record has been created and validated, and that
        if it fails to do so, that I'm alerted so I can log it. 
 
    """
    brokenfile = open("/Users/peder/dev/goc/broken-pilot-records.xml", "w")
    brokenfile.write("<XML>\n")
    cnt = Counter()
    def __init__(self, datafile):
        self.holdings = PilotHoldings()
        self.data = common.XmlStreamReader("RECORD",datafile)
        for i,node in enumerate(self.data.elements()):          
            try:
                self.holdings.add_record(node)
            except Exception  as e:
                print e
                self.cnt[e.type]+=1
                #self.__write_errors(e)
                pass
                
        print self.cnt.items()
        #self.holdings.pickle_it()
    #This is cheezy, I should be using a yield statement inside a generator for this
    brokenfile.write("</XML>\n")
    
    def __write_errors(self,error):
        # this is where logging belongs
        print "--- {} Error ----".format(error.type)
        print error.message
        self.brokenfile.write(lxml.etree.tostring(error.node)+"\n")      
        
    def report(self):
        self.holdings.report('full')
    def test(self):
        # This will fail, so we must alther the holdings to make it pass
        self.holdings.test() 
    def match_languages(self):
        file = open("/Users/peder/dev/goc/matched-pilot-records.xml", "w")
        file.write("<XML>\n")
        lang_counts = Counter()
        match_count = 0
        #print title[0]
        language_markers=[
                    (' - English Version',' - French Version'),
                    (' (in English)', ' (in French)'),
                    ('(- English)', '(- French)'),  
                    (' (English Version)',' (French Version)')]
  

        ''' If one of these markers is in the data,
            then there is probably a french equivalent
        '''  
        for i,record in enumerate(self.holdings.records):   
            lang_counts[record.language]+=1               
            for marker in language_markers:
               
                if marker[0] in record.title_en:
                   
                    # Split the marker out of the record
                    split_title_en = record.title_en.split(marker[0])[0]
                    equivalent_title_french_record = split_title_en + marker[1]
                    #print equivalent_title_french_record
                    # Having this title should enable us to find the french record
                    # in the many cases where it's not alternating with the english
                    
                    french_record =  self.holdings.find_french_record(equivalent_title_french_record)

                    try:
                        #print marker
                        e = str(record.title_en.split(marker[0])[0])
                        f = str(french_record[0].title_en.split(marker[1])[0])
#                        print e
#                        print f
#                        print i, record.node 
#                        print i, french_record[0].node
                        if e == f:
                            print "Match", record.node
#                            print i, "WE HAVE A MATCH " + match_count

                            file.write(lxml.etree.tostring(record.node)+"\n")
                            file.write(lxml.etree.tostring(french_record[0].node)+"\n")
                            #file.write(french_record[0].node + "\n")
                            match_count +=1
                            break
                        
                    except:
                        pass
                        #print i, "NONE"
                        #print "No match for " + split_title_en
                        #raise
                        
                    #search holdings for the french record
                    #sys.exit()
                    break
        file.write("</XML>\n")
        file.close()
        print "LANGUAGE COUNTS", lang_counts.items()
        print "MATCH COUNT ", match_count
if __name__ == "__main__":
     
    print "Report"
    pilot_file =  "/Users/peder/dev/goc/OD_DatasetDump-0.xml" 
    pilot = PilotDelegator(pilot_file)
    pilot.report()
    pilot.match_languages()