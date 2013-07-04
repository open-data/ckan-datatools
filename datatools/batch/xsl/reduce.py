''' Reducing complex XML files to something more simple '''
from lxml import etree
import sys
import lxml
from string import Template


def polygon(context, points):
    
    points = points.split(" ")
    extent_template = Template('''{"type": "Polygon", "coordinates": [[[$minx, $miny], [$minx, $maxy], [$maxx, $maxy], [$maxx, $miny], [$minx, $miny]]]}''')
    return extent_template.substitute(
                                minx = points[0],
                                miny = points[1],
                                maxx = points[2],
                                maxy = points[3]
                                )

def nap_reduce(file,transform):
    class FileResolver(etree.Resolver):
        def resolve(self, url, pubid, context):
            return self.resolve_filename(url, context)



    #prefixmap = {'f':'http://www.jakobsen.ca/myfunctions'}
    parser = etree.XMLParser()
    ns = etree.FunctionNamespace('http://www.jakobsen.ca/myfunctions')
    ns['polygon'] = polygon
    ns.prefix = 'pj'
    parser.resolvers.add(FileResolver())
    xml_input = etree.parse(open(file,'r'), parser)
    xslt_root = etree.parse(open(transform,'r'), parser)
    transform = etree.XSLT(xslt_root)
    # Get the node tree that results from the transformation
    result = transform(xml_input)
    
    # Set up function namespace

    
   
    print str(result)
    #
    #print str()


if __name__ == '__main__':
   file = "iso19139.xml"
   transform = 'iso19139.xsl'
   #transform='json.xsl'
   nap_reduce(file,transform)

   
   # main()