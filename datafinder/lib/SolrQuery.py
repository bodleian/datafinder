from datafinder.config import settings
import json

class SolrQuery():
    def __init__(self, query_filter = "" , q = "*:*" , req_format="json"):         
            solr_params = {}
            solr_params['q'] = q.encode('utf-8')+query_filter 
            solr_params['wt'] = req_format
            self.solr_reponse={}
            try:
                solr_conn, b = settings.getSolrConnection()
                solr_response = solr_conn.raw_query(**solr_params)
                print solr_response
                search = json.loads(solr_response)
                self.solr_reponse = search['response']
            except:
                pass
                  
    
    def get_solrresponse(self):
        return  self.solr_reponse 
    
    def get_NumRecordsFound(self):
        numFound = 0
        if 'numFound' in  self.solr_reponse:
            numFound = self.solr_reponse.get('numFound',0)
            return numFound

    