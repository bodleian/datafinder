<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:fund="http://vocab.ox.ac.uk/projectfunding#"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dcterms="http://purl.org/dc/terms/" xmlns:oxds="http://vocab.ox.ac.uk/dataset/schema#"
    xmlns:bibo="http://purl.org/ontology/bibo/"
    xmlns:ads="http://archaeologydataservice.ac.uk/advice/archiveSchema" version="2.0"
    xmlns:GEO="http://www.w3.org/2003/01/geo/wgs84_pos#"
    exclude-result-prefixes="ads">

    <xsl:output method="xml" indent="yes" doctype-public="http://www.w3.org/2001/XMLSchema-instance"
        name="xml"/>

    <xsl:template match="/">
        <xsl:for-each select="//ads:archive">


            <rdf:RDF xmlns:fund="http://vocab.ox.ac.uk/projectfunding#"
                xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                xmlns:dcterms="http://purl.org/dc/terms/"
                xmlns:oxds="http://vocab.ox.ac.uk/dataset/schema#"
                xmlns:bibo="http://purl.org/ontology/bibo/"
                xmlns:GEO="http://www.w3.org/2003/01/geo/wgs84_pos#">


                <rdf:Description rdf:about="">

                    <xsl:if test="exists(ads:title)">
                        <dcterms:title>
                            <xsl:value-of select="ads:title"/>
                        </dcterms:title>
                    </xsl:if>

                    <xsl:if test="exists(ads:description)">
                        <dcterms:description>
                            <xsl:value-of select="ads:description"/>
                        </dcterms:description>
                    </xsl:if>

                    <xsl:apply-templates select="ads:Coverage/ads:subjects/ads:subject"/>

                    <xsl:if test="exists(ads:language)">
                        <dcterms:language>
                            <xsl:value-of select="ads:language"/>
                        </dcterms:language>
                    </xsl:if>

                    <xsl:apply-templates select="ads:Actors/ads:actor/ads:name"/>

                    <xsl:if test="exists(ads:published/ads:firstReleased)">
                        <dcterms:issued>
                            <xsl:value-of select="ads:published/ads:firstReleased"/>
                        </dcterms:issued>
                    </xsl:if>

                    <xsl:if test="exists(ads:created/ads:from)">
                        <oxds:dataCollectedStart>
                            <xsl:value-of select="ads:created/ads:from"/>
                        </oxds:dataCollectedStart>
                    </xsl:if>

                    <xsl:if test="exists(ads:created/ads:to)">
                        <oxds:dataCollectedEnd>
                            <xsl:value-of select="ads:created/ads:to"/>
                        </oxds:dataCollectedEnd>
                    </xsl:if>

                    <xsl:if test="exists(ads:Coverage/ads:temporal/ads:dateRange/ads:startYear)">
                        <oxds:dataCoverageStart>
                            <xsl:value-of
                                select="ads:Coverage/ads:temporal/ads:dateRange/ads:startYear"/>
                        </oxds:dataCoverageStart>
                    </xsl:if>

                    <xsl:if test="exists(ads:Coverage/ads:temporal/ads:dateRange/ads:endYear)">
                        <oxds:dataCoverageEnd>
                            <xsl:value-of
                                select="ads:Coverage/ads:temporal/ads:dateRange/ads:endYear"/>
                        </oxds:dataCoverageEnd>
                    </xsl:if>
                    
                    <xsl:apply-templates
                        select="ads:Coverage/ads:locations/ads:location"/>

                    <xsl:apply-templates
                        select="ads:Coverage/ads:coordinates/ads:world/ads:latitude"/>

                    <xsl:apply-templates
                        select="ads:Coverage/ads:coordinates/ads:world/ads:longitude"/>
                    <dcterms:status/>

                    <xsl:if test="exists(ads:doi)">
                        <bibo:doi>
                            <xsl:value-of select="ads:doi"/>
                        </bibo:doi>
                    </xsl:if>

                    <xsl:apply-templates select="ads:types/ads:type"/>

                    <xsl:apply-templates
                        select="ads:Files/ads:dissemination/ads:category/ads:fileType"/>

                    <xsl:if test="exists(ads:version)">
                        <oxds:currentversion>
                            <xsl:value-of select="ads:version"/>
                        </oxds:currentversion>
                    </xsl:if>

                    <xsl:apply-templates select="ads:Actors/ads:actor[@type='funder']"/>

               <xsl:if test="exists(ads:licence)">
                        <dcterms:license>
                            <xsl:value-of select="ads:licence"/>
                        </dcterms:license>
                    </xsl:if>

                </rdf:Description>


            </rdf:RDF>
        </xsl:for-each>
    </xsl:template>



    <xsl:template match="ads:actor[@type='funder']">
        <fund:FundingBody>
            <xsl:value-of select="ads:organisation/text()"/>
        </fund:FundingBody>
    </xsl:template>

    <xsl:template match="ads:latitude">
        <GEO:lat>
            <xsl:value-of select="text()"/>
        </GEO:lat>
    </xsl:template>

    <xsl:template match="ads:Actors/ads:actor/ads:name">
        <dcterms:creator>
            <xsl:value-of select="text()"/>
        </dcterms:creator>
    </xsl:template>

    <xsl:template match="ads:types/ads:type">
        <dcterms:type>
            <xsl:value-of select="text()"/>
        </dcterms:type>
    </xsl:template>

    <xsl:template match="ads:Files/ads:dissemination/ads:category/ads:fileType">

        <dcterms:format>
            <xsl:value-of select="ads:extension/text()"/>
        </dcterms:format>

        <oxds:Filesize>
            <xsl:value-of select="ads:size/text()"/>
        </oxds:Filesize>

    </xsl:template>


    <xsl:template match="ads:longitude">
        <GEO:lng>
            <xsl:value-of select="text()"/>
        </GEO:lng>
    </xsl:template>

    <xsl:template match="ads:Coverage/ads:locations/ads:location">
        <dcterms:location>
            <xsl:value-of select="text()"/>
        </dcterms:location>
    </xsl:template>

    <xsl:template match="ads:subject">
        <dcterms:subject>
            <xsl:value-of select="@type"/>
        </dcterms:subject>
        <dcterms:keywords>
            <xsl:value-of select="text()"/>
        </dcterms:keywords>
    </xsl:template>




</xsl:stylesheet>
