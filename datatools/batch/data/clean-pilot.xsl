<?xml version="1.0" encoding="UTF-8" ?>
<!--
    clean-pilot
-->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:output encoding="UTF-8" indent="yes" method="xml" />
<!--
    <xsl:template match="/">
    	
    		<xsl:for-each select="root/record"> 
    			<record>   
    					
    			<title><xsl:value-of select="FORM[NAME=*]/A" /></title> 
    			<foo><xsl:value-of select="FORM/*" /></foo>     		
    		</xsl:for-each>
    	</record>
    </xsl:template>
-->
<xsl:output omit-xml-declaration="yes" indent="yes"/>
<xsl:strip-space elements="*"/>

<xsl:variable name='FieldNames' select='document("fields.xml")' />
<!-- Remove the stuff we don't want -->
<xsl:template match="NAME" /><!-- without this, you'll get everything on one line. Why? -->
<xsl:template match="Q" />
<xsl:template match="A" />

<!-- Select all non empty records.  
This is where it would be nice to pass a list with XSLT 2.0 -->
<xsl:template match="A[.!='']">	
	<xsl:variable name="field-name" select="following-sibling::NAME"/>
	<xsl:element name="{$field-name}">
		<xsl:value-of select="."/>
	</xsl:element>	
</xsl:template>

<xsl:template match="record">
	<record>
		<xsl:apply-templates select="FORM" />
	</record>
</xsl:template>

<xsl:template match="root">
	<records>
		<xsl:apply-templates select="record" />
	</records>
</xsl:template>

</xsl:stylesheet>