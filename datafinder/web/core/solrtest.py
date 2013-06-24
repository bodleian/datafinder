from solr import SolrConnection
import json, traceback
from datetime import  date, timedelta

def SolrQuery(query_filter = "" , q = "*:*" , req_format="json", type="dataset"):
            numFound=0
            solr_params = {}
            solr_params['q'] = q.encode('utf-8')+query_filter+ " AND type:"+type
            solr_params['wt'] = req_format
            try:
                solr_conn = SolrConnection("http://10.0.0.154:8081/solr")
                solr_response = solr_conn.raw_query(**solr_params)
                #print solr_response
                search = json.loads(solr_response)
                solr_reponse = search['response']
                #print solr_response
                numFound = 0
                if 'numFound' in  solr_reponse:
                    numFound = solr_reponse.get('numFound',0)
                    print numFound
            except:
                traceback.print_exc()
                print "exception"
                pass
            return (solr_response,numFound)

if __name__ == '__main__':
    context = {}
    end = date.today()
    start = end-timedelta(days=7)
    #SolrQuery(self, query_filter = "" , q = "*:*" , req_format="json")

    #(solr_response,numFound) = SolrQuery()
    #context['numFound'] = numFound

    #query = "timestamp:["+ str(start) + "T00:00:00Z" + " TO "+ str(end) + "T00:00:00Z" + "]"
    #print "your query = " + query
    #(solr_response,numFound) = SolrQuery(q = query)

    #context['numFoundThisWeek'] = numFound
    
    
    
    

