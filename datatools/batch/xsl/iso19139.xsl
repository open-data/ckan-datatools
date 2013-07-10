
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
                version="1.0"

	xmlns:gmd="http://www.isotc211.org/2005/gmd"
	xmlns:xlink="http://www.w3.org/1999/xlink" 
	xmlns:gco="http://www.isotc211.org/2005/gco"
	xmlns:gml="http://www.opengis.net/gml"
	xmlns:od="http://data.gc.ca/functions"
	exclude-result-prefixes="gmd xlink gco gml od"
	>

<xsl:template match="/" xml:space="preserve">   
<package>
<id><xsl:value-of select="//gmd:fileIdentifier"/></id>
<owner_org>ec</owner_org>
<title><xsl:value-of select="//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString"></xsl:value-of></title>
<title_fra><xsl:value-of select="//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString"/></title_fra>
<notes>
	<xsl:value-of select="od:make_notes(//gmd:abstract/gco:CharacterString/text(),//gmd:supplementalInformation/gco:CharacterString/text())" />
</notes>
<notes_fra>
	<xsl:value-of select="od:make_notes(//gmd:abstract/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString/text(),//gmd:supplementalInformation/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString/text())"/>
</notes_fra>
<catalog_type>Geo Data | G\xe9o</catalog_type>
<subject><xsl:value-of select="//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:topicCategory/gmd:MD_TopicCategoryCode"/></subject>
<topic_category><xsl:value-of select="//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:topicCategory/gmd:MD_TopicCategoryCode"/></topic_category>
<keywords><xsl:for-each select="//gmd:keyword"><xsl:value-of select="gco:CharacterString"/>, </xsl:for-each></keywords>
<keywords_fra><xsl:for-each select="//gmd:keyword"><xsl:value-of select="gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString"/>, </xsl:for-each></keywords_fra>
<license_id>ca-ogl-lgo</license_id>
<geographic_region><xsl:value-of select="//gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:type/gmd:MD_KeywordTypeCode[@codeListValue='place']/../../gmd:keyword/gco:CharacterString"/></geographic_region>
<spatial><xsl:apply-templates select="//gmd:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox"/></spatial>
<spatial_representation_type><xsl:value-of select="//gmd:MD_SpatialRepresentationTypeCode"/></spatial_representation_type>
<presentation_form><xsl:value-of select="//gmd:CI_PresentationFormCode"/></presentation_form>
<browse_graphic_url><xsl:value-of select="//gmd:MD_BrowseGraphic/gmd:fileName/gco:CharacterString"/></browse_graphic_url>
<date_published><xsl:value-of select="//gmd:CI_Date/gmd:date/gco:Date"/></date_published>
<date_modified></date_modified>
<maintenance_and_update_frequency><xsl:value-of select="//gmd:MD_MaintenanceFrequencyCode/@codeListValue"/></maintenance_and_update_frequency>
<data_series_name><xsl:call-template name="extract-data-series-name">
	<xsl:with-param name='fullstring' select="//gmd:supplementalInformation/gco:CharacterString" />
</xsl:call-template></data_series_name>
<data_series_name_fra><xsl:call-template name="extract-data-series-name">
		<xsl:with-param name='fullstring' select="//gmd:supplementalInformation/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString[@locale='#FRE']" />
	</xsl:call-template></data_series_name_fra>
	
<data_series_issue_identification></data_series_issue_identification>
<data_series_issue_identification_fra></data_series_issue_identification_fra>
<digital_object_identifier></digital_object_identifier>

<time_period_coverage_start><xsl:value-of select="//gml:TimePeriod/gml:beginPosition"/></time_period_coverage_start>
<time_period_coverage_end><xsl:value-of select="//gml:TimePeriod/gml:endPosition" /></time_period_coverage_end>
<url><xsl:apply-templates select="//gmd:supplementalInformation/gco:CharacterString" /></url>
<url_fra><xsl:apply-templates select='//gmd:supplementalInformation/gmd:PT_FreeText/gmd:textGroup'/></url_fra>
<endpoint_url></endpoint_url>
<endpoint_url_fra></endpoint_url_fra>
<ready_to_publish>True</ready_to_publish>
<portal_release_date>2013-06-18</portal_release_date>

<!-- RESOURCES -->
<resources>
<xsl:for-each select="//gmd:onLine">
	<resource>

        <name><xsl:value-of select="od:resource_name_from_name('eng',gmd:CI_OnlineResource/gmd:name/gco:CharacterString/text())"/></name>
        <name_fra><xsl:value-of select="od:resource_name_from_name('fra',gmd:CI_OnlineResource/gmd:name/gco:CharacterString/text())"/></name_fra>
        <resource_type><xsl:value-of select="od:resource_type_from_name(gmd:CI_OnlineResource/gmd:name/gco:CharacterString/text())"/></resource_type>
        <url><xsl:value-of select="gmd:CI_OnlineResource/gmd:linkage/gmd:URL"/></url>
        <size><xsl:value-of select="od:size_from_name(gmd:CI_OnlineResource/gmd:name/gco:CharacterString/text())"/></size>
        <format><xsl:value-of select="od:format_from_url(gmd:CI_OnlineResource/gmd:linkage/gmd:URL/text())"/></format>
        <language><xsl:value-of select="od:language_from_name(@xlink:role)"/></language>

		<!--
        <name><xsl:value-of select="gmd:CI_OnlineResource/gmd:name/gco:CharacterString"/></name>
        <name_fra><xsl:value-of select="gmd:CI_OnlineResource/gmd:name/gco:CharacterString"/></name_fra>
        <resource_type><xsl:value-of select="gmd:name/gco:CharacterString"/></resource_type>
        <url><xsl:value-of select="gmd:CI_OnlineResource/gmd:linkage/gmd:URL"/></url>
        <size><xsl:value-of select="gmd:CI_OnlineResource/gmd:name/gco:CharacterString"/></size>
        <format><xsl:value-of select="gmd:CI_OnlineResource/gmd:name/gco:CharacterString"/></format>
        <language><xsl:value-of select="@xlink:role"/></language>
		-->
	</resource>
</xsl:for-each>
</resources>
</package>
</xsl:template>

<!-- XSL Templates -->
<!-- spatial -->
<xsl:template match="gmd:EX_GeographicBoundingBox">
  <xsl:call-template name="polygon">
  	<xsl:with-param name="points"><xsl:for-each select="//gco:Decimal"><xsl:value-of select="."/>, </xsl:for-each></xsl:with-param>
  </xsl:call-template>
</xsl:template>
<xsl:template name="polygon">
	<xsl:param name="points"/>
	<xsl:value-of select="od:polygon($points)"/>
</xsl:template>
<!-- Extract URLs from Freeform text  -->
<xsl:template match="gmd:supplementalInformation/gco:CharacterString">
	<xsl:call-template name="extract-2nd-url">
  		<xsl:with-param name='fullstring' select="." />
	</xsl:call-template>
</xsl:template>
<xsl:template match="gmd:LocalisedCharacterString[@locale='#FRE']">
	<xsl:call-template name="extract-2nd-url">
  		<xsl:with-param name='fullstring' select="." />
	</xsl:call-template>
</xsl:template>

<xsl:template name="extract-data-series-name">
	<xsl:param name="fullstring" />
    <xsl:value-of select="substring-after(substring-before($fullstring,' - '),':')"/>
</xsl:template>
<xsl:template name="extract-2nd-url">
	<xsl:param name="fullstring" />
    http:<xsl:value-of select="substring-after(substring-after($fullstring,'http:'),'http:')"/>
</xsl:template>
<!--  -->

</xsl:stylesheet>