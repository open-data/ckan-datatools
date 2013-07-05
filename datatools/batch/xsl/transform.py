"""
Use saxon to do XSLT with Jython
See http://codingwithpassion.blogspot.com/2011/03/saxon-xslt-java-example.html
 
Pass in arguments
 
	- 1 xslt
	- 2 xml source
	- 3 xml output
 
"""
 
from java.io import File;
from javax.xml.transform import Transformer;
from javax.xml.transform import TransformerFactory;
from javax.xml.transform.stream import StreamResult;
from javax.xml.transform.stream import StreamSource;
from java.io import StringWriter;
import os
import sys
 
xslt = File(sys.argv[1])
tFactory = TransformerFactory.newInstance()
transformer = tFactory.newTransformer(StreamSource(xslt))
writer = StringWriter();
out = transformer.transform(
							StreamSource(File(
								sys.argv[2]
								)),
					        StreamResult(
					        	File(sys.argv[3])
					        )
					       )
out2 = transformer.transform(
							StreamSource(File(
								sys.argv[2]
								)),
					         StreamResult(writer)
					       )
 
#print out
print writer
