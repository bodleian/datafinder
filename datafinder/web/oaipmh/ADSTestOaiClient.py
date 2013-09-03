import lxml.etree as ET
from urllib import urlretrieve, urlcleanup
from datetime import datetime
import uuid
import os
import unittest
import sys
sys.path.append("../..")
sys.path.append("../../lib")
import logging
import shutil
#from logging import handlers
import logging.config
#from LogConfigParser import Config
import urllib2
import base64
import urllib
#from multipart import MultiPartFormData
import SparqlQueryTestCase
from HTTP_request import HTTPRequest
from xslt import  XSLT
class TestOaiClient(unittest.TestCase):
        

    def tearDown(self):
        return
    
    def setUp(self, datefile=None):
        self.until = datetime.now().strftime("%Y-%m-%d")
        #print "Sdsdsdsds"
        self.metadata_formats = ['oai_dc', 'mets']
        self.verbs = ['Identify', 'ListIdentifiers', 'ListRecords', 'ListSets', 'ListMetadataFormats', 'GetRecord']
        self.args = {'from':None, 'until':self.until}
        self.oai_ns = "{http://www.openarchives.org/OAI/2.0/}"
        #self.silo = "sandbox"
  #  eprints-maths_sources = {
  #  'maths':{'base':"http://eprints.maths.ox.ac.uk/cgi/oai2", 'records_base':'http://eprints.maths.ox.ac.uk/'}
  # ,'sbs' : {'args':"set=6F72613D54525545", 'base':"http://eureka.sbs.ox.ac.uk/cgi/oai2", 'records_base':'http://eureka.sbs.ox.ac.uk/'}
  # ,'economics':{'base':"http://economics.ouls.ox.ac.uk/cgi/oai2", 'records_base':'http://economics.ouls.ox.ac.uk/'}
  # }
        #self.source = {'base':"http://eprints.maths.ox.ac.uk/cgi/oai2", 'records_base':'http://eprints.maths.ox.ac.uk/'}
        self.source = {'base':"http://archaeologydataservice.ac.uk/oai/archives/OAIHandler", 'records_base':'http://archaeologydataservice.ac.uk/'}
        self.identifiers = []
        self.delete_identifiers = []

        self.LastModifiedFile = None
        if datefile:
              self.LastModifiedFile = datefile
        
        self.datadir = None    
        self.ids_data_file = None
        self.dc_data_file = None
        self.mods_data_file = None

        self.types = {
            'Conference or Workshop Item':'conference_item'
            ,'Monograph':'monograph'
            ,'Book':'book'
            ,'Book Section':'book_section'
            ,'Thesis':'thesis'
            ,'Article':'article'
            ,'Other':'general_item'
            ,'Artefact':'general_item'
            ,'Show/Exhibition':'general_item'
            ,'Patent':'general_item'
            ,'Teaching Resource':'general_item'
            ,'Experiment':'general_item'
            ,'Audio':'general_item'
            ,'Dataset':'general_item'
            ,'Video':'general_item'
            ,'Composition':'general_item'
            ,'Performance':'general_item'
            ,'Image':'general_item'
            ,'Technical Report':'report'
        }
		
        #c = Config()
        #logbase = c.get("app:main", "bulkuploadlog.dir")
        #logfile = os.path.join(logbase, 'bulk_uploads_logging.conf')
        #logging.config.fileConfig(logfile)
        self.logger = logging.getLogger('root')
        #oai_listIdentifiers(src=self.source)

    def set_datadir(self, pid):
#    def set_datadir(self):
        self.tmpdir = '/tmp/silos'
        if os.path.isdir(self.tmpdir):
           shutil.rmtree(self.tmpdir)
        os.mkdir(self.tmpdir)    
        self.datadir = '/tmp/silos/%s'%pid
        #self.datadir = '/tmp/'
        if os.path.isdir(self.datadir):
            shutil.rmtree(self.datadir)
        os.mkdir(self.datadir)        
        self.data_file = '%s/data_file.rdf'%self.datadir
        self.dc_data_file = '%s/dc_manifest_file.rdf'%self.datadir
        self.mods_data_file = '%s/mods_data_file'%self.datadir
        self.ads_xslt_file = './ads2df.xsl'

    def set_from(self):
        if not os.path.isfile(self.LastModifiedFile):
            return False
        f = open(self.LastModifiedFile, 'r')
        startdate = f.read()
        startdate = startdate.strip().strip('\n')
        f.close()
        self.args['from'] = startdate
        return True

    def update_until(self):
        f = open(self.LastModifiedFile, 'w')
        f.write(self.until)
        f.close()
        return

     
    #def oai_listIdentifiers(self, src={'base':"http://eprints.maths.ox.ac.uk/cgi/oai2", 'records_base':'http://eprints.maths.ox.ac.uk/'}, resumptionToken=None):
    def oai_listIdentifiers(self, src={'base':"http://archaeologydataservice.ac.uk/oai/archives/OAIHandler", 'records_base':'https://archaeologydataservice.ac.uk/'}, resumptionToken=None):
        self.ids_data_file = '/tmp/ids_data_file' ##'/tmp/%s_ids_data_file'%unicode(uuid.uuid4())
        src_url = None
        if resumptionToken:
            src_url = "%s?verb=ListIdentifiers&resumptionToken=%s"%(src['base'], resumptionToken)
        else:
            src_url = "%s?verb=ListIdentifiers&metadataPrefix=ads_archive"%src['base']
            for arg, val in self.args.iteritems():
                if val:
                    src_url = "%s&%s=%s"%(src_url, arg, val)
            if 'args' in src:
                src_url = "%s&%s"%(src_url,src['args'])
        tries = 1
        while tries < 11:
            urlretrieve(src_url, self.ids_data_file)
            if os.path.isfile(self.ids_data_file):
                self.logger.info("Downloaded identifiers for %s - %s"%(src['base'], src_url))
                break
            self.logger.warn("Error retreiving identifiers for %s - %s (try # %d)"%(src['base'], src_url, tries))
            tries += 1
        urlcleanup()
        tree = ET.ElementTree(file=self.ids_data_file)
        rt = tree.getroot()
        ids = rt.findall("%(ns)sListIdentifiers/%(ns)sheader/%(ns)sidentifier"%{'ns':self.oai_ns})
        #self.oai_createSilo("eprints-maths")
        for ID in ids:
             if resumptionToken and 'deletion' in resumptionToken:
                self.delete_identifiers.append(ID.text)
             else:
                 self.identifiers.append(ID.text)
                 self.oai_createDataset( src, "ADS", ID.text)
                 break
                 
        rtoken = rt.findall("%(ns)sListIdentifiers/%(ns)sresumptionToken"%{'ns':self.oai_ns})
         #os.remove(self.ids_data_file)
        if rtoken:
             self.oai_listIdentifiers(src, resumptionToken=rtoken[0].text)
        #shutil.rmtree(self.tmpdir)

        # Create empty test submission dataset
    def oai_createDataset(self, src, silo, identifier, embargoed=False, embargoed_until=False):
        # Create a new dataset, check response
        
        id = self.oai_getDCMetadata(src, identifier, silo)

        fields = \
            [ ("id",id)           ]
        if embargoed != None:
            if embargoed:
                fields.append(('embargoed', 'True'))
        else:
                fields.append(('embargoed', 'False'))
        if embargoed_until != None:
            if embargoed_until == True:
                fields.append(('embargoed_until', 'True'))
            elif embargoed_until == False:
                fields.append(('embargoed_until', 'False'))
            else:
                fields.append(('embargoed_until', embargoed_until))

        dc_manifest_file = open(self.dc_data_file).read()
        user_name = 'admin'
        password = 'test'
        host = 'datafinder-d2v.bodleian.ox.ac.uk'
        http_host = 'http://datafinder-d2v.bodleian.ox.ac.uk'

        # Post the harvested oai_dc metadata file to the dataset
        fields=[]
        files = [ ("file", "dc_manifest_file.rdf", dc_manifest_file, "application/rdf+xml")]
        (reqtype, reqdata) = SparqlQueryTestCase.encode_multipart_formdata(fields, files)
        postRequest = HTTPRequest(endpointhost=host)        
        postRequest.setRequestUserPass(endpointuser=user_name, endpointpass=password)      
        (resp,respdata) = postRequest.doHTTP_POST(reqdata, reqtype, resource="/ADS/datasets/" + id + "/")
        

        #Submit the main manifest file which as the see also
        fields=[]
        main_manifest_filename = 'manifest.rdf'
        main_manifest = open(main_manifest_filename).read()

        #print main_manifest

        files =  [("file", "manifest.rdf", main_manifest, "application/rdf+xml")]            
        (reqtype, reqdata) = SparqlQueryTestCase.encode_multipart_formdata(fields, files)                
        (resp,respdata) = postRequest.doHTTP_POST(reqdata, reqtype, resource="/ADS/datasets/" + id + "/")
        
        return
        
   
        
    def oai_getDCMetadata(self, src, identifier, silo):
        #Get the OAI record from the source
        src_url = "%s?verb=GetRecord&metadataPrefix=ads_archive&identifier=%s"%(src['base'], identifier)
        df_identifier_list = identifier.split(':')
        df_identifier = df_identifier_list[2]
        self.set_datadir(df_identifier)
        tries = 1
        while tries < 11:
            if os.path.isfile(self.data_file):
                self.logger.info("Downloaded DC for %s - %s"%(identifier, silo))
                break
            urlretrieve(src_url, self.data_file)
            self.logger.error("Error retreiving DC for %s - %s (try # %d)"%(identifier, silo, tries))
            tries += 1
        urlcleanup()
        dc_file = open(self.data_file, 'r')
        buffer = dc_file.read()
        newbuffer= buffer.replace('OAI-PMH xmlns', 'OAI-PMH xmlns:ads="http://archaeologydataservice.ac.uk/advice/archiveSchema" xmlns')
        dc_file.close()
        
        dc_file = open(self.data_file, 'w+')
        dc_file.write(newbuffer)
        dc_file.close() 
              
    
        # Run the transforms        
        xslt = XSLT( "saxon9he.jar" )

        xslt.generate( self.data_file, self.ads_xslt_file, output_file=self.dc_data_file)
     
#        dom1 = ET.parse(self.data_file)
#        dom = ET.tostring(dom1, pretty_print=True)
#        xslt1 = ET.parse(self.ads_xslt_file)
#        xslt = ET.tostring(xslt1, pretty_print=True)
#        
#        transform = ET.XSLT(ET.XML(xslt))        
#        dom = ET.XML(dom)
#        transform = ET.XSLT(xslt1)   
#       
#        dom = ET.XML( '<a><b>Text</b></a>' )
#        xslt = ET.XML(  '<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"><xsl:template match="/"><foo><xsl:value-of select="/a/b/text()" /></foo></xsl:template></xsl:stylesheet>')     
#        transform = ET.XSLT( xslt )
#        
#        
#        
#        newdom = transform(dom1)
#
#        print str(newdom)
#        
#        print "printing ... "
#        print ET.tostring(newdom, pretty_print=True)
#        
#        oai_dc_file = open(self.dc_data_file, 'w+')
#        oai_dc_file.write(ET.tostring(newdom, pretty_print=True))
#        oai_dc_file.close();
        return df_identifier

    def testUnits(self):
        assert (True)

    def testComponents(self):
        assert (True)

    def testIntegration(self):
        assert (True)

    def testPending(self):
        assert (False), "No pending test"

# Assemble test suite

import TestUtils

def getTestSuite(select="unit"):
    """
    Get test suite

    select  is one of the following:
            "unit"      return suite of unit tests only
            "component" return suite of unit and component tests
            "all"       return suite of unit, component and integration tests
            "pending"   return suite of pending tests
            name        a single named test to be run
    """
    testdict = {
        "unit": 
            [ 
             "oai_listIdentifiers"
            ],
        "component":
            [ "testComponents"
            ],
        "integration":
            [ "testIntegration"
            ],
        "pending":
            [ "testPending"
            ]
        }
    return TestUtils.getTestSuite(TestOaiClient, testdict, select=select)

# Run unit tests directly from command line
if __name__ == "__main__":
    TestUtils.runTests("TestOaiClient.log", getTestSuite, sys.argv)

# End.



   
