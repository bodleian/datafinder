import xml.etree.ElementTree as ET
from urllib import urlretrieve, urlcleanup
import json, os
import sys
sys.path.append("../..")
sys.path.append("../../lib")
import logging
import SparqlQueryTestCase
from HTTP_request import HTTPRequest

def oai_getDCRecord(src, identifier):
	oai_ns = "{http://www.openarchives.org/OAI/2.0/}"
	src_url = "%s?verb=GetRecord&metadataPrefix=oai_dc&identifier=%s"%(src['base'], identifier)
	tries = 1
	dc_data_file = '/tmp/%s.dc'%identifier
	while tries < 11:
		if os.path.isfile(dc_data_file):
			break
		urlretrieve(src_url, dc_data_file)
		tries += 1
	dc = None
	if not os.path.isfile(dc_data_file):
		return dc
	tree = ET.ElementTree(file=dc_data_file)
	rt = tree.getroot()
	#Define namespaces and add them to element tree, so it uses them.
	namespaces = {
		'oai_dc':"http://www.openarchives.org/OAI/2.0/oai_dc/"
		,'dc':"http://purl.org/dc/elements/1.1/"
		,'xsi':"http://www.w3.org/2001/XMLSchema-instance"
	}
	for k,v in namespaces.iteritems():
		ET._namespace_map[v] = str(k)
	oai_dc = rt.find("%(ns)sGetRecord/%(ns)srecord/%(ns)smetadata/{%(oai_dc)s}dc"%{'ns':oai_ns,'oai_dc':namespaces['oai_dc']})
	#oai_dc.append(ET.SubElement(oai_dc, "{http://purl.org/dc/elements/1.1/}doi"))

	#print dc
	return oai_dc

		# Create empty test submission dataset
def oai_createDataset( src, silo, id, metadata,  embargoed=None, embargoed_until=None):
		# Create a new dataset, check response
		#metadata = oai_getDCRecord(src, identifier)
		dc_data_file = 'dc_manifest_file.rdf'
		oai_dc_file = open(dc_data_file, 'w+')
		oai_dc_file.write(metadata)
		oai_dc_file.close()#ET.tostring(oai_dc)
		#metadata = self.oai_getDCMetadata(src, identifier, silo)
		
		#id = id.replace('.','-')
		fields = \
			[ ("id",id)
#			  ("source", metadata["source"]),
#			  ("creator", metadata["creator"]),
#			  ("subject", metadata["subject"]),
#			  ("date",metadata["date"]),
#			  ("relation", metadata["relation"]),
#			  ("title", metadata["title"]),
#			  ("type", metadata["type"])
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

		dc_manifest_file = open(dc_data_file).read()
		user_name = 'admin'
		password = 'test'
		host = 'datafinder-d2v.bodleian.ox.ac.uk'
		http_host = 'http://datafinder-d2v.bodleian.ox.ac.uk'
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

		#print "METADATA TO BE MUNGED" + metadata_content
		#print "resource url: /ww1archives/datasets/"+id+"/manifest.rdf"

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
		
if __name__ == '__main__':	
	f = open('ww1archivesIdsWithDOI.json', 'r')
	ans = json.load(f)
	f.close()
	len(ans)
	src = {'base':"https://databank.ora.ox.ac.uk/oaipmh", 'records_base':'https://databank.ora.ox.ac.uk/'}
	count = 1
	silo = 'ww1archives'
	for identifier in ans:
		oai_dc = oai_getDCRecord(src, identifier)
		#doi
		sid = oai_dc.findall("{http://purl.org/dc/elements/1.1/}identifier")
#		doi_element = ET.SubElement(oai_dc, "{http://purl.org/dc/elements/1.1/}doi")
#		doi =  list(set([id.text for id in sid if id.text.startswith("doi")]))[0]
#		print doi
#		doi = doi.replace('doi:','')
#		doi_element.text = doi
		
		oai_dc_string = ET.tostring(oai_dc)
#		print "OAI_DC TREE before:   " + oai_dc_string
		oai_dc_string=oai_dc_string.replace("oai_dc:dc","rdf:RDF")
		oai_dc_string=oai_dc_string.replace('xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">', '><rdf:Description rdf:about="">')
		oai_dc_string=oai_dc_string.replace('xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/  http://www.openarchives.org/OAI/2.0/oai_dc.xsd"','')
		#oai_dc_string=oai_dc_string.replace('xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/"','')
		#oai_dc_string=oai_dc_string.replace('http://www.openarchives.org/OAI/2.0/oai_dc.xsd', '')
		oai_dc_string=oai_dc_string.replace('xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"', 'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"')
		oai_dc_string=oai_dc_string.replace("</rdf:RDF>","</rdf:Description></rdf:RDF>")
		metadata = oai_dc_string
#		print "OAI_DC TREE after:   " + metadata
		
		
		#Identifier
		
		ids = repr(sid)
		#print list(set([id.text for id in sid if id.text.startswith("ww")]))
		id =  list(set([id.text for id in sid if id.text.startswith("ww")]))[0]
		oai_createDataset(src, silo, id ,oai_dc_string)
		count += 1
		if count > 1000:
			break
