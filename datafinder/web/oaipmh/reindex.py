import sys
sys.path.append("/var/www/datafinder/datafinder/lib")
from broadcast import BroadcastToRedis
from HTTP_request import HTTPRequest
sys.path.append("/var/www/datafinder/datafinder/message_workers")
from redis import Redis
from redisqueue import RedisQueue
from solr import SolrConnection
from LogConfigParser import Config
from collections import defaultdict
from solrFields import solr_fields_mapping
import json, rdflib
import ast

def gather_document(silo_name, uuid, item_id,  graph):
    #graph = item.get_graph()
    document = defaultdict(list)
    #document['uuid'].append(item.metadata['uuid'])
    document['uuid'].append(uuid)
    document['id'].append(item_id)
    document['silo'].append(silo_name)
    #for (_,p,o) in graph.triples((URIRef(item.uri), None, None)):
    for (_,p,o) in graph.triples((None , None, None)):
        if str(p) in solr_fields_mapping:
            field = solr_fields_mapping[str(p)]
            #if field == "aggregatedResource":
            #    if '/datasets/' in o:
            #        fn = unicode(o).split('/datasets/')
            #        if len(fn) == 2 and fn[1]:
            #           document['filename'].append(unicode(fn[1]).encode("utf-8"))
            if field == "embargoedUntilDate":
                ans = u"%sZ"%unicode(o).split('.')[0]
                document[field].append(unicode(ans).encode("utf-8"))
            else:
                document[field].append(unicode(o).encode("utf-8"))
        else:
            document['text'].append(unicode(o).encode("utf-8"))
    document = dict(document)
    return document

if __name__ == "__main__":
 
    solrurl = "http://localhost:8081/solr"
    user_name = 'admin' 
    password = 'test'
    datastore = HTTPRequest(endpointhost='10.0.1.154')       
    datastore.setRequestUserPass(endpointuser=user_name, endpointpass=password) 
    
    (resp,silostr) = datastore.doHTTP_GET(resource="/silos" , expect_type="application/JSON")
    silos = ast.literal_eval(silostr)
    print "silos = " + str(silos)
    silos=['DataFinder']
    for silo in silos:
        print "Currently addressing silo = " + silo
        (resp,datasetsstr) = datastore.doHTTP_GET(resource="/" + silo + "/datasets", expect_type="application/JSON")
        
        datasets = ast.literal_eval(datasetsstr)
        
        for dataset in datasets:
            print "dataset =  " + dataset
            item_id = dataset
            (resp,respdata) = datastore.doHTTP_GET(resource="/" + silo +"/states/" + item_id )
            #print "/" + silo +"/states/" + item_id
            #print str(respdata)
            json_data = json.loads(respdata)
            uuid = json_data['state']['metadata']['uuid']
                        
            (resp,respdata) = datastore.doHTTP_GET(resource="/" + silo +"/datasets/" + item_id +"/df_manifest.rdf")
            #print respdata
            text_file = open("sample_redis_manifest.rdf", "w")
            text_file.write(respdata)
            text_file.close()
            graph=rdflib.Graph()
            try:
                with open("sample_redis_manifest.rdf", 'r') as f:
                     graph.parse(f, base="sample_redis_manifest.rdf")
            except IOError, e:
                pass
        
            solr = SolrConnection(solrurl)
            solr_doc = gather_document(silo , uuid , item_id,  graph )
            print solr_doc
            #solr_doc = ast.literal_eval(solr_doc_str)
#            solr_doc = {'status': ['seeking_approval'],
#                        'alternative': [''], 
#                        'identifier': ['fgdfg'], 
#                        'aggregatedResource': ['http://datafinder-d2v.bodleian.ox.ac.uk/DataFinder/datasets/fgdfg/df_manifest.rdf'], 'mediator': ['admin'], 'text': ['http://vocab.ox.ac.uk/projectfunding#', '', '', '', '', '', 'yes', ''], 
#                        'depositor': ['zool0982'], 
#                        'language': [''], 
#                        'embargoedUntilDate': ['2083-06-21T08:56:50Z'], 
#                        'id': ['fgdfg'], 
#                        'subject': [''], 
#                        'publisher': ['', 'Bodleian Libraries, University of Oxford'], 
#                        'rights': ['http://ora.ouls.ox.ac.uk/objects/uuid%3A1d00eebb-8fed-46ad-8e38-45dbdb4b224c'],
#                        'uuid': [u'655325fe9036441fb275bc2292e40e1d'], 
#                        'license': ['CC0 1.0 Universal (CC0 1.0). See http://creativecommons.org/publicdomain/zero/1.0/legalcode'], 
#                        'title': ['fgdfg'], 
#                        'embargoStatus': ['True'], 
#                        'description': [''], 
#                        'format': [''], 
#                        'modified': ['2013-06-21 08:56:50.308522'], 
#                        'created': ['2013-06-21 08:56:50.049645'], 
#                        'currentVersion': ['2'], 
#                        'issued': [''], 
#                        'silo': ['DataFinder'], 
#                        'type': ['', 'http://vocab.ox.ac.uk/dataset/schema#DataSet']
#                         }


            solr_doc =  solr.add(_commit=True, **(solr_doc))
            solr.commit()
