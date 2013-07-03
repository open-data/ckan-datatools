''' Reducing complex XML files to something more simple '''
from lxml import etree
import sys
import lxml


def nap_reduce(file,transform):
    class FileResolver(etree.Resolver):
        def resolve(self, url, pubid, context):
            return self.resolve_filename(url, context)

    parser = etree.XMLParser()
    parser.resolvers.add(FileResolver())
    xml_input = etree.parse(open(file,'r'), parser)
    xslt_root = etree.parse(open(transform,'r'), parser)
    transform = etree.XSLT(xslt_root)
    result = transform(xml_input)
    
    #print dir(result)
    print str(result)
    #
    #print str()


if __name__ == '__main__':
   file = "/Users/peder/dev/OpenData/data_sources/ec/export-full-1370459620522/01f628bd-344c-438a-922b-43bd10c6da5e/metadata/metadata.iso19139.xml"
   transform = 'iso19139.xsl'
   #transform='json.xsl'
   nap_reduce(file,transform)

   
   # main()