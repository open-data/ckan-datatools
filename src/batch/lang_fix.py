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
        #print title[0]
        english_record_markers=[
                    'English Version',
                    ' (in English)',
                    ' (in French)',
                    '(- English)',
                    ' - English',      
                    ' (English Version)']
        ''' If one of these markers is in the data,
            then there is probably a french equivalent
        '''                       
        for marker in english_record_markers:
                
            if marker in self.title_en:
                print self.title_en
                break

if __name__ == "__main__":
     
    print "Report"
    pilot_file =  "/Users/peder/dev/goc/OD_DatasetDump-0-partial.xml" 
    pilot = PilotDelegator(pilot_file)
    pilot.report()