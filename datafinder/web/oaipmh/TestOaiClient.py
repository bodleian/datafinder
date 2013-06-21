import xml.etree.ElementTree as ET
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
import base64, json
import urllib
#from multipart import MultiPartFormData
import SparqlQueryTestCase
from HTTP_request import HTTPRequest
   
class TestOaiClient(unittest.TestCase):
        

    def tearDown(self):
        return
    
    def setUp(self, datefile=None):
        self.until = datetime.now().strftime("%Y-%m-%d")#%H:%M:%SZ")
        print "Sdsdsdsds"
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
        self.source = {'base':"https://databank.ora.ox.ac.uk/oaipmh", 'records_base':'https://databank.ora.ox.ac.uk/'}
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
    def oai_listIdentifiers(self, src={'base':"https://databank.ora.ox.ac.uk/oaipmh", 'records_base':'https://databank.ora.ox.ac.uk/'}, resumptionToken=None):
        self.ids_data_file = '/tmp/ids_data_file' ##'/tmp/%s_ids_data_file'%unicode(uuid.uuid4())
        src_url = None
        if resumptionToken:
            src_url = "%s?verb=ListIdentifiers&resumptionToken=%s"%(src['base'], resumptionToken)
        else:
            src_url = "%s?verb=ListIdentifiers&metadataPrefix=oai_dc"%src['base']
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
        self.logger.info('After cleanup')
        tree = ET.ElementTree(file=self.ids_data_file)
        rt = tree.getroot()
        ids = rt.findall("%(ns)sListIdentifiers/%(ns)sheader/%(ns)sidentifier"%{'ns':self.oai_ns})
        self.logger.info('IDs = ' + str(ids))
        #self.oai_createSilo("eprints-maths")
#        for ID in ids:
#             self.logger.info('ID = ' +str(ID))
#             if resumptionToken and 'deletion' in resumptionToken:
#                self.delete_identifiers.append(ID.text)
#             else:
#                 self.identifiers.append(ID.text)
#                 self.oai_createDataset( src, "ww1archives", ID.text)
                 #break
                 
        f = open('ww1archivesIdsWithDOI.json', 'r')
        ans = json.load(f)
        f.close()
        len(ans)
        count = 0
        for identifier in ans:
            self.oai_createDataset( src, "ww1archives", identifier)
                 
#        rtoken = rt.findall("%(ns)sListIdentifiers/%(ns)sresumptionToken"%{'ns':self.oai_ns})
#         #os.remove(self.ids_data_file)
#        if rtoken:
#             self.oai_listIdentifiers(src, resumptionToken=rtoken[0].text)
        #shutil.rmtree(self.tmpdir)

    def oai_getTitle(self, src, identifier):
        #Get the OAI record from the source
        src_url = "%s?verb=GetRecord&metadataPrefix=oai_dc&identifier=%s"%(src, identifier)
        tries = 1
        while tries < 11:
            urlretrieve(src_url, self.dc_data_file)
            if os.path.isfile(self.dc_data_file):
                self.logger.info("Downloaded DC for %s"%(identifier))
                break
            self.logger.error("Error retreiving DC for %s (try # %d)"%(identifier, tries))
            tries += 1
        urlcleanup()
        #Parse the document using element tree, so we can extract just the tags under oai_dc
        tree = ET.ElementTree(file=self.dc_data_file)
        rt = tree.getroot()

        #Define namespaces and add them to element tree, so it uses them.
        namespaces = {
            'oai_dc':"http://www.openarchives.org/OAI/2.0/oai_dc/"
            ,'dc':"http://purl.org/dc/elements/1.1/"
            ,'xsi':"http://www.w3.org/2001/XMLSchema-instance"
        }

        for k,v in namespaces.iteritems():
            ET._namespace_map[v] = str(k)

        #Get the DC metadata from the data
        oai_dc = rt.find("%(ns)sGetRecord/%(ns)srecord/%(ns)smetadata/{%(oai_dc)s}dc"%{'ns':self.oai_ns,'oai_dc':namespaces['oai_dc']})

        #The titles are listed as dc:title in the metadata. Get them
        record_titles = oai_dc.findall("{http://purl.org/dc/elements/1.1/}title")
        titles = []
        for t in record_titles:
            if t.text:
                titles.append(t.text)
        return titles
    
      
    def oai_createSilo(self, silo):
        #Get the OAI record from the source
        req = urllib2.Request("http://192.168.2.216/admin")
        USER = "admin"
        PASS = "test"
        auth = 'Basic ' + base64.urlsafe_b64encode("%s:%s" % (USER, PASS))
        req.add_header('Authorization', auth)
        req.add_header('Accept', 'application/JSON')
        accepted_params = ['title', 'description', 'notes', 'owners', 'disk_allocation', 'administrators', 'managers', 'submitters']
        req.add_data(urllib.urlencode({'silo': silo}))      
        ans = urllib2.urlopen(req)
        print 'SERVER RESPONSE:'
        ans.read()  
        return 
    
        # Create empty test submission dataset
    def oai_createDataset(self, src, silo, identifier, embargoed=None, embargoed_until=None):
        # Create a new dataset, check response
        
        metadata = self.oai_getDCMetadata(src, identifier, silo)
        id = metadata["identifier"]
        #id = id.replace('.','-')
        fields = \
            [ ("id",id)
#              ("source", metadata["source"]),
#              ("creator", metadata["creator"]),
#              ("subject", metadata["subject"]),
#              ("date",metadata["date"]),
#              ("relation", metadata["relation"]),
#              ("title", metadata["title"]),
#              ("type", metadata["type"])
            ]
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
        host = 'datafinder-d2v'
        http_host = 'http://datafinder-d2v'
        # Create a dataset
        files =[]
        (reqtype, reqdata) = SparqlQueryTestCase.encode_multipart_formdata(fields, files)
        postRequest = HTTPRequest(endpointhost=host)        
        postRequest.setRequestUserPass(endpointuser=user_name, endpointpass=password)      
        (resp,respdata) = postRequest.doHTTP_POST(
            reqdata, reqtype, 
            resource="/ww1archives/datasets/")
        
        # Post the harvested oai_dc metadata file to the dataset
        fields=[]
        files = \
            [ ("file", "dc_manifest_file.rdf", dc_manifest_file, "application/rdf")
            ]
        (reqtype, reqdata) = SparqlQueryTestCase.encode_multipart_formdata(fields, files)
        postRequest = HTTPRequest(endpointhost=host)        
        postRequest.setRequestUserPass(endpointuser=user_name, endpointpass=password)      
        (resp,respdata) = postRequest.doHTTP_POST(
            reqdata, reqtype, 
            resource="/ww1archives/datasets/"+id)
        
        #<rdf:Description rdf:resource="http://example.org/testrdf.zip">
        # Add the dc:relation into the main manifest file that related to the oai_dc manifest file

        
        fields=[ ("relation", "/ww1archives/datasets/"+id+"/dc_manifest_file.rdf")]
        files =[]
        metadata_content = """<rdf:RDF
  xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
  xmlns:rdfs='http://www.w3.org/2000/01/rdf-schema#'
>

  <rdf:Description rdf:about="">
    <rdfs:seeAlso rdf:resource="dc_manifest_file.rdf"/>
  </rdf:Description>
</rdf:RDF>"""

        print "METADATA TO BE MUNGED" + metadata_content
        print "resource url: /ww1archives/datasets/"+id+"/manifest.rdf"

        putRequest = HTTPRequest(endpointhost=host)        
        putRequest.setRequestUserPass(endpointuser=user_name, endpointpass=password)      
        (resp,respdata) = putRequest.doHTTP_PUT(
            metadata_content,
            resource="/ww1archives/datasets/"+id+"/manifest.rdf")
        #(reqtype, reqdata) = SparqlQueryTestCase.encode_multipart_formdata(fields, files)
        #
        
        # os.remove(self.dc_data_file)
        
        #LHobtained = resp.getheader('Content-Location', None)
        #LHexpected = "%sdatasets/TestSubmission"%self._endpointpath
        #self.assertEquals(LHobtained, LHexpected, 'Content-Location not correct')
        return
        
#  <rdfs:seeAlso rdf:resource=" """+http_host+"/eprints-maths/datasets/"+id+"/dc_manifest_file.rdf"+""" "/>
#  <rdf:Description rdf:about=" """+http_host+"""/eprints-maths/datasets/"""+id+""" ">
# xmlns:dcterms='http://purl.org/dc/terms/'
#  xmlns:oxds='http://vocab.ox.ac.uk/dataset/schema#'
#  xmlns:ore='http://www.openarchives.org/ore/terms/'
    def oai_mungeMetadata(self):
        host = '192.168.2.216'
        http_host = 'http://192.168.2.216'   
        user_name = 'admin'
        password = 'test'
        id="oai:generic-eprints-org:1086"
        fields=[ ("relation", "/ww1archives/datasets/"+id+"/dc_manifest_file.rdf")]
        files =[]
        metadata_content = """<rdf:RDF
  xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
  xmlns:rdfs='http://www.w3.org/2000/01/rdf-schema#'
>
  <rdf:Description rdf:about="">
    <rdfs:seeAlso  rdf:resource="dc_manifest_file.rdf" />
  </rdf:Description>
</rdf:RDF>"""

        #print "METADATA TO BE MUNGED" + metadata_content
       # print "resource url: /eprints-maths/datasets/"+id+"/manifest.rdf"
#(resp, respdata) = datastore.doHTTP_PUT(metadata_content, resource="/sandbox/datasets/TestSubmission/manifest.rdf", expect_type="text/plain")


        #(reqtype, reqdata) = SparqlQueryTestCase.encode_multipart_formdata(fields, files)
        putRequest = HTTPRequest(endpointhost=host)        
        putRequest.setRequestUserPass(endpointuser=user_name, endpointpass=password)      
        (resp,respdata) = putRequest.doHTTP_PUT(
            metadata_content,
            resource="/ww1archives/datasets/"+id+"/manifest.rdf")
        
        # os.remove(self.dc_data_file)
        
        #LHobtained = resp.getheader('Content-Location', None)
        #LHexpected = "%sdatasets/TestSubmission"%self._endpointpath
        #self.assertEquals(LHobtained, LHexpected, 'Content-Location not correct')
        return
        
    def oai_getDCMetadata(self, src, identifier, silo):
        #Get the OAI record from the source
        src_url = "%s?verb=GetRecord&metadataPrefix=oai_dc&identifier=%s"%(src['base'], identifier)
        self.set_datadir(identifier)
        tries = 1
        while tries < 11:
            if os.path.isfile(self.data_file):
                self.logger.info("Downloaded DC for %s - %s"%(identifier, silo))
                break
            urlretrieve(src_url, self.data_file)
            self.logger.error("Error retreiving DC for %s - %s (try # %d)"%(identifier, silo, tries))
            tries += 1
        urlcleanup()
        #Parse the document using element tree, so we can extract just the tags under oai_dc
        tree = ET.ElementTree(file=self.data_file)
        print tree
        rt = tree.getroot()

        #Define namespaces and add them to element tree, so it uses them.
        namespaces = {
            'oai_dc':"http://www.openarchives.org/OAI/2.0/oai_dc/"
            ,'dc':"http://purl.org/dc/elements/1.1/"
            ,'xsi':"http://www.w3.org/2001/XMLSchema-instance"
        }

        for k,v in namespaces.iteritems():
            ET._namespace_map[v] = str(k)

        #Get the ID from the data header
        #Don't need to find this as ID is passed as parameter to function
        record_id = rt.find("%(ns)sGetRecord/%(ns)srecord/%(ns)sheader/%(ns)sidentifier"%{'ns':self.oai_ns})
        if record_id:
            ID = record_id.text

        #Get the DC metadata from the data
        record_metadata = rt.find("%(ns)sGetRecord/%(ns)srecord/%(ns)smetadata"%{'ns':self.oai_ns})
        #oai_dc = rt.find("%(ns)sGetRecord/%(ns)srecord/%(ns)smetadata/{%(oai_dc)s}dc"%{'ns':self.oai_ns,'oai_dc':namespaces['oai_dc']})
        #oai_dc_string = ET.tostring(oai_dc)
        #oai_dc_string=oai_dc_string.replace("oai_dc:dc","rdf:RDF")
        #oai_dc_string=oai_dc_string.replace('xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', '')
        #oai_dc_string=oai_dc_string.replace('xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd">', '><rdf:Description rdf:about="">')
        #oai_dc_string=oai_dc_string.replace('xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"', 'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"')
        #oai_dc_string=oai_dc_string.replace("</rdf:RDF>","</rdf:Description></rdf:RDF>")
        
        #print "OAI_DC TREE:   " + ET.tostring(oai_dc)
        
#        oai_dc_file = open(self.dc_data_file, 'w+')
#        oai_dc_file.write(record_metadata)#ET.tostring(oai_dc)
#        #The files are listed as identifiers in the metadata. Get them and remove the id tags
#        record_ids = oai_dc.findall("{http://purl.org/dc/elements/1.1/}identifier")
#        files = []
#        for rid in record_ids:
#            if rid.text and rid.text and rid.text.startswith('http://eureka'):
#                files.append(rid.text)
#            oai_dc.remove(rid)
#
#        #The types are listed as dc:type in the metadata. Get them
#        record_types = oai_dc.findall("{http://purl.org/dc/elements/1.1/}type")
#        types = []
#        for typ in record_types:
#            if typ.text and typ.text.strip() in self.types:
#                types.append(self.types[typ.text.strip()])
#        type = (' '.join(types)).strip()       
#        #Title
#        #The titles are listed as dc:title in the metadata. Get them
#        record_titles = oai_dc.findall("{http://purl.org/dc/elements/1.1/}title")
#        titles = []
#        for t in record_titles:
#            if t.text:
#                titles.append(t.text)
#        title = (' '.join(titles)).strip()  
#
#        #Identifier
#        sid = ET.SubElement(oai_dc, "{http://purl.org/dc/elements/1.1/}identifier")
#        sid.text = identifier
#
#        #Add the source identifier in relation
#        sid = identifier.split(':')[-1]
#        relele = ET.SubElement(oai_dc, "{http://purl.org/dc/elements/1.1/}relation")
#        relele.text = "%s%s"%(src['records_base'], sid)
#        relation = relele.text
#
#        #Source
#        sid = identifier.split(':')[-1]
#        srcele = ET.SubElement(oai_dc, "{http://purl.org/dc/elements/1.1/}source")
#        srcele.text = src['records_base']
#        source = srcele.text  
#        
#        #Creator
#        creat = oai_dc.findall("{http://purl.org/dc/elements/1.1/}creator")
#        creat_or =[]
#        for c in creat:
#            if c.text:
#                creat_or.append(c.text)
#        creator = (' '.join(creat_or)).strip()  
#        
#        #Subject
#        sub = oai_dc.findall("{http://purl.org/dc/elements/1.1/}subject")
#        subj =[]
#        for s in sub:
#            if s.text:
#                subj.append(s.text)
#        subject = (' '.join(subj)).strip()  
#        #Date
#        dat = oai_dc.findall("{http://purl.org/dc/elements/1.1/}date")
#        dates =[]
#        for d in dat:
#            if d.text:
#                dates.append(d.text)
#        date = (' '.join(dates)).strip()  
#        #Write oai_dc to the file oai_dc.xml. 
#        #metadata_tree = ET.ElementTree(element=oai_dc)
#        #metadata_tree.write('oai_dc.xml')
#
#        #Write the dc element to string
#        dc = None
#        dc = ET.tostring(oai_dc)
#        if not dc:
#            self.logger.warn('NO DC record for %s - %s'%(identifier, silo))
#        else:
#            self.logger.info('Retreived DC record for %s - %s'%(identifier, silo))
#                
#        #Return dc and list of files
#        print  {'dc':dc, 'files':files, 'types':types, 'titles':titles}
#        #return {'dc':dc, 'files':files, 'types':types, 'titles':titles}
#        
#
#        metadata={'identifier':identifier,
#                  'source':source,
#                  'creator':creator,
#                  'subject':subject,
#                  'date':date,
#                  'relation':relation,
#                  'title':title,    
#                  'type':type          
#                  }
#        print "Metadata : " + repr(metadata)
        return record_metadata

    
    def oai_getDCRecord(self, src, identifier, pid):
        #Get the OAI record from the source
        src_url = "%s?verb=GetRecord&metadataPrefix=oai_dc&identifier=%s"%(src['base'], identifier)
        self.set_datadir(pid)
        req = urllib2.Request("http://192.168.2.216/admin")
        USER = "admin"
        PASS = "test"
        auth = 'Basic ' + base64.urlsafe_b64encode("%s:%s" % (USER, PASS))
        req.add_header('Authorization', auth)
        req.add_header('Accept', 'application/JSON')
        accepted_params = ['title', 'description', 'notes', 'owners', 'disk_allocation', 'administrators', 'managers', 'submitters']
        req.add_data(urllib.urlencode({'silo': pid}))      
        ans = urllib2.urlopen(req)
        print 'SERVER RESPONSE:'
        ans.read()
        tries = 1
        while tries < 11:
            if os.path.isfile(self.dc_data_file):
                self.logger.info("Downloaded DC for %s - %s"%(identifier, pid))
                break
            urlretrieve(src_url, self.dc_data_file)
            self.logger.error("Error retreiving DC for %s - %s (try # %d)"%(identifier, pid, tries))
            tries += 1
        urlcleanup()
        #Parse the document using element tree, so we can extract just the tags under oai_dc
        tree = ET.ElementTree(file=self.dc_data_file)
        rt = tree.getroot()

        #Define namespaces and add them to element tree, so it uses them.
        namespaces = {
            'oai_dc':"http://www.openarchives.org/OAI/2.0/oai_dc/"
            ,'dc':"http://purl.org/dc/elements/1.1/"
            ,'xsi':"http://www.w3.org/2001/XMLSchema-instance"
        }

        for k,v in namespaces.iteritems():
            ET._namespace_map[v] = str(k)

        #Get the ID from the data header
        #Don't need to find this as ID is passed as parameter to function
        #record_id = rt.find("%(ns)sGetRecord/%(ns)srecord/%(ns)sheader/%(ns)sidentifier"%{'ns':self.oai_ns})
        #if record_id:
        #    ID = record_id.text

        #Get the DC metadata from the data
        #record_metadata = rt.find("%(ns)sGetRecord/%(ns)srecord/%(ns)smetadata"%{'ns':self.oai_ns})
        oai_dc = rt.find("%(ns)sGetRecord/%(ns)srecord/%(ns)smetadata/{%(oai_dc)s}dc"%{'ns':self.oai_ns,'oai_dc':namespaces['oai_dc']})

        #The files are listed as identifiers in the metadata. Get them and remove the id tags
        record_ids = oai_dc.findall("{http://purl.org/dc/elements/1.1/}identifier")
        files = []
        for rid in record_ids:
            if rid.text and rid.text and rid.text.startswith('http://eureka'):
                files.append(rid.text)
            oai_dc.remove(rid)

        #The types are listed as dc:type in the metadata. Get them
        record_types = oai_dc.findall("{http://purl.org/dc/elements/1.1/}type")
        types = []
        for typ in record_types:
            if typ.text and typ.text.strip() in self.types:
                types.append(self.types[typ.text.strip()])

        #The titles are listed as dc:title in the metadata. Get them
        record_titles = oai_dc.findall("{http://purl.org/dc/elements/1.1/}title")
        titles = []
        for t in record_titles:
            if t.text:
                titles.append(t.text)

        #Add the pid
        sid = ET.SubElement(oai_dc, "{http://purl.org/dc/elements/1.1/}identifier")
        sid.text = pid

        #Add the source identifier in relation
        sid = identifier.split(':')[-1]
        relele = ET.SubElement(oai_dc, "{http://purl.org/dc/elements/1.1/}relation")
        relele.text = "%s%s"%(src['records_base'], sid)

        #Add the source
        sid = identifier.split(':')[-1]
        srcele = ET.SubElement(oai_dc, "{http://purl.org/dc/elements/1.1/}source")
        srcele.text = src['records_base']

        #Write oai_dc to the file oai_dc.xml. 
        #metadata_tree = ET.ElementTree(element=oai_dc)
        #metadata_tree.write('oai_dc.xml')

        #Write the dc element to string
        dc = None
        dc = ET.tostring(oai_dc)
        if not dc:
            self.logger.warn('NO DC record for %s - %s'%(identifier, pid))
        else:
            self.logger.info('Retreived DC record for %s - %s'%(identifier, pid))

        #Return dc and list of files
        return {'dc':dc, 'files':files, 'types':types, 'titles':titles}


    def oai_getMetsModsRecord(self, src, identifier, pid):
        #example record with file "oai:eureka.sbs.ox.ac.uk:325"
        src_url = "%s?verb=GetRecord&metadataPrefix=mets&identifier=%s"%(src['base'], identifier)
        tries = 1
        while tries < 11:
            urlretrieve(src_url, self.mods_data_file)
            if os.path.isfile(self.mods_data_file):
                self.logger.info("Downloaded MODS for %s - %s"%(identifier, pid))
                break
            self.logger.error("Error retreiving MODS for %s - %s (try # %d)"%(identifier, pid, tries))
            tries += 1
        urlcleanup()
    
        #Parse the document using element tree, so we can extract just the tags under mets
        tree = ET.ElementTree(file=self.mods_data_file)
        rt = tree.getroot()

        #Define namespaces and add them to element tree, so it uses them.
        namespaces = {
            'oai_dc':"http://www.openarchives.org/OAI/2.0/oai_dc/"
            ,'mets':"http://www.loc.gov/METS/"
            ,'mods':"http://www.loc.gov/mods/v3"
            ,'xlink':"http://www.w3.org/1999/xlink"
            ,'xsi':"http://www.loc.gov/standards/mets/mets.xsd http://www.loc.gov/mods/v3 http://www.loc.gov/standards/mods/v3/mods-3-0.xsd"
        }
        for k,v in namespaces.iteritems():
            ET._namespace_map[v] = str(k)
        
        #Get the MODS metadata from the data
        mets_mods = rt.find("%(ns)sGetRecord/%(ns)srecord/%(ns)smetadata/{%(mets)s}mets/{%(mets)s}dmdSec/{%(mets)s}mdWrap/{%(mets)s}xmlData"%{'ns':self.oai_ns,'mets':namespaces['mets']})

        #Add the pid
        spid = ET.SubElement(mets_mods, "{http://www.loc.gov/mods/v3}identifier",  attrib={"type":"pid"})
        spid.text = pid
        surn = ET.SubElement(mets_mods, "{http://www.loc.gov/mods/v3}identifier",  attrib={"type":"urn"})
        surn.text = pid

        #Add the source id as another version
        sid = identifier.split(':')[-1]
        sida = ET.SubElement(mets_mods, "{http://www.loc.gov/mods/v3}relatedItem",  attrib={"type":"otherVersion"})
        sidb = ET.SubElement(sida, "{http://www.loc.gov/mods/v3}location")
        sidc = ET.SubElement(sidb, "{http://www.loc.gov/mods/v3}url")
        sidc.text = "%s%s"%(src['records_base'], sid)

        #Add the source as record content source
        srcele = ET.SubElement(mets_mods, "{http://www.loc.gov/mods/v3}recordInfo")
        srceleb = ET.SubElement(srcele, "{http://www.loc.gov/mods/v3}recordContentSource")
        srceleb.text = src['records_base']

        #Write the mods element to string and replace mets tag with mods tag
        MODS = None
        MODS = ET.tostring(mets_mods)
        if not MODS:
            self.logger.warn('NO MODS record for %s - %s'%(identifier, pid))
        else:
            self.logger.info('Retreived MODS record for %s - %s'%(identifier, pid))
        MODS = MODS.replace("""<mets:xmlData xmlns:mets="http://www.loc.gov/METS/">""", """<mods:modsCollection xmlns:mods="http://www.loc.gov/mods/v3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/mods/v3 http://ora.ox.ac.uk/access/mods-3.2-oxford.xsd">
  <mods:mods version="3.2">""")
        MODS = MODS.replace("""</mets:xmlData>""", """
  </mods:mods>
</mods:modsCollection>""")

        #Get the list of files
        files = []
        mets_files = rt.findall("%(ns)sGetRecord/%(ns)srecord/%(ns)smetadata/{%(mets)s}mets/{%(mets)s}fileSec/{%(mets)s}fileGrp/{%(mets)s}file"%{'ns':self.oai_ns,'mets':namespaces['mets']})
        for m in mets_files:
            size = m.get('SIZE')
            mt = m.get('MIMETYPE')
            flocat = m.find("{%(mets)s}FLocat"%{'mets':namespaces['mets']})
            loc = flocat.get('{%(xlink)s}href'%{'xlink':namespaces['xlink']})
            files.append((loc, mt, size))
        return {'mods':MODS, 'files':files}
    
    def retreiveFiles(self, files):
        files_retreived = []
        for f in files:
            fn = f[0].strip('/').split('/')[-1]
            floc = '%s/%s'%(self.datadir, fn)
            tries = 1
            while True:
                urlretrieve(f[0], floc)
                if os.path.isfile(floc):
                    if str(os.path.getsize(floc)) == f[2]:
                        urlcleanup()
                        self.logger.info('Retreived file %s'%f[0])
                        break
                    else:
                        self.logger.warn('Download file size does not match metadata %s (try # %d)'%(f[0], tries))
                else:
                    self.logger.warn('Error retreiving file %s (try # %d)'%(f[0], tries))
                tries += 1
                if tries > 10:
                    break
            files_retreived.append((f[0], f[1], f[2], floc))
        return files_retreived


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



   
