<?xml version="1.0"?>
<!-- XSLT 1.0 -->
<!--- This is a bad idea to use XSLT to produce JSON, because the nodes can't be natively built and parsed out - use pyhton -->
<xsl:stylesheet version="1.0" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
	xmlns:gmd="http://www.isotc211.org/2005/gmd"
	xmlns:xlink="http://www.w3.org/1999/xlink" 
	xmlns:gco="http://www.isotc211.org/2005/gco">
    <xsl:output method="text" omit-xml-declaration="yes" indent="no"/>
    <xsl:template match="/">
        <xsl:apply-templates select="//gmd:onLine"/>
        <xsl:text></xsl:text>
    </xsl:template>
    
	<xsl:template match="gmd:onLine">
		
		<xsl:text>{- ===}</xsl:text>
		<xsl:value-of select="."/>
		"url": "<xsl:value-of select="gmd:CI_OnlineResource/gmd:linkage/gmd:URL"/>",
   	</xsl:template>    
   
</xsl:stylesheet>