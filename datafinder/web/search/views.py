# Mako templating engine
from djangomako.shortcuts import render_to_response, render_to_string
from django.conf import settings
from django.template import RequestContext
import sys, json
sys.path.append("../..")
from datafinder.lib.search_term import term_list
from datafinder.lib.conneg import MimeType as MT, parse as conneg_parse
from datafinder.config import settings
from urllib import urlencode, unquote, quote
import logging    


def searchtips(request):
    context = { 
        #'DF_VERSION':settings.DF_VERSION,
        #'STATIC_URL': settings.STATIC_URL,3
        'silo_name':"",
        'ident' : "",
        'id':"",
        'path' :"",
        'user_logged_in_name':"",
        'q':"",
        'typ':"",
        }
    return render_to_response('searchtips.html',context, context_instance=RequestContext(request))
    #return render_to_response('home.html',context, context_instance=RequestContext(request))
    
    
def raw(request):
        ident = request.environ.get('repoze.who.identity')  
        context['ident'] = ident

        silos = None
        if ag.metadata_embargoed:
            if not ident:
                abort(401, "Not Authorised")
            silos = ag.authz(ident)

        if silos and not isinstance(silos, basestring) and type(silos).__name__ == 'list':
            silos = ' '.join(silos)
               
        http_method = request.environ['REQUEST_METHOD']        
        if http_method == "GET":
            params = request.GET
        elif http_method == "POST":
            params = request.POST

        if not "q" in params:
            abort(400, "Parameter 'q' is not available")

        #If ag.metadata_embargoed, search only within your silos
        if params['q'] == '*':
            if silos:
                params['q'] = """silo:(%s)"""%silos
            else:
                params['q'] = "*:*"
        elif silos and not 'silo:' in params['q']:
            params['q'] = """%s AND silo:(%s)"""%(params['q'], silos)        

        accept_list = None
        if 'wt' in params and params['wt'] == "json":
            accept_list = [MT("application", "json")]
        elif 'wt' in params and params['wt'] == "xml":
            accept_list = [MT("text", "xml")]
        else:                       
            if 'HTTP_ACCEPT' in request.environ:
                try:
                    accept_list = conneg_parse(request.environ['HTTP_ACCEPT'])
                except:
                    accept_list= [MT("text", "html")]
            if not accept_list:
                accept_list= [MT("text", "html")]

            mimetype = accept_list.pop(0)
            while(mimetype):
                if str(mimetype).lower() in ["text/html", "text/xhtml"]:
                    params['wt'] = 'json'
                    accept_list= [MT("text", "html")]
                    break                 
                elif str(mimetype).lower() in ["text/plain", "application/json"]:
                    params['wt'] = 'json'
                    accept_list= [MT("application", "json")]
                    break
                elif str(mimetype).lower() in ["application/rdf+xml", "text/xml"]:
                    params['wt'] = 'xml'
                    accept_list = [MT("text", "xml")]
                    break
                # Whoops - nothing satisfies
                try:
                    mimetype = accept_list.pop(0)
                except IndexError:
                    mimetype = None

        if not 'wt' in params or not params['wt'] in ['json', 'xml']:
            params['wt'] = 'json'
            accept_list= [MT("text", "html")]        
        if not 'fl' in params or not params['fl']:
            #Also include the following fields - date modified, publication year / publication date, embargo status, embargo date, version
            params['fl'] = "id,silo,mediator,creator,title,score"
        if not 'start' in params or not params['start']:
            params['start'] = '0'
        if not 'rows' in params or not params['rows']:
            params['rows'] = '100'
        try:            
            result = ag.solr.raw_query(**params)
        except:
            result = {}
        
        mimetype = accept_list.pop(0)
        while(mimetype):
            if str(mimetype).lower() in ["text/html", "text/xhtml"]:
                context['result'] = result                    
                return render('/raw_search.html')        
            elif str(mimetype).lower() in ["text/plain", "application/json"]:
                response.content_type = 'application/json; charset="UTF-8"'
                response.status_int = 200
                response.status = "200 OK"
                return result
            elif str(mimetype).lower() in ["application/rdf+xml", "text/xml"]:
                response.content_type = 'text/xml; charset="UTF-8"'
                response.status_int = 200
                response.status = "200 OK"
                return result
            # Whoops - nothing satisfies
            try:
                mimetype = accept_list.pop(0)
            except IndexError:
                mimetype = None
        #Whoops - nothing staisfies - default to text/html
        context['result'] = result         
        return render('/raw_search.html')


def detailed(request,query=None, additional_fields=[]):
    
        context = { 
            #'DF_VERSION':settings.DF_VERSION,
            #'STATIC_URL': settings.STATIC_URL,
            'silo_name':"",
            'ident' : "",
            'id':"",
            'path' :"",
            'user_logged_in_name':"",
            'q':"",
            'typ':"",
            'docs':"",
            }

        context['all_fields'] = term_list().get_all_search_fields()
        context['field_names'] = term_list().get_search_field_dictionary()
        context['facetable_fields'] = term_list().get_all_facet_fields()
        context['types'] = term_list().get_type_field_dictionary()
        context['search_fields'] = ['silo', 'id', 'title', 'uuid', 'embargoStatus', 'embargoedUntilDate', 'currentVersion', 'doi', 'publicationDate', 'abstract', 'description', 'creator', 'isVersionOf', 'isPartOf', 'subject', 'type']
        context['sort_options'] = {'score desc':'Relevance',  'publicationDate desc':'Date (Latest to oldest)','publicationDate asc':'Date (Oldest to Latest)','silo asc':'Silo A to Z','silo desc':'Silo Z to A'}

        if query:
            context['q'] = query
        else:        
            context['q'] = request.REQUEST.get('q',None)
        try:
            context['q'] = unquote(context['q'])
        except:
            pass

        context['typ'] = 'all'
        if request.REQUEST.get("type",None):
            context['typ'] = request.REQUEST.get("type",None)

        if not context['q'] or context['q'] == '*' or context['q'] == "":
            context['q'] = "*:*"
 
        # Search controls
        truncate = request.REQUEST.get('truncate', None)
        start = request.REQUEST.get('start', None)
        rows = request.REQUEST.get('rows', None)
        sort = request.REQUEST.get('sort', None)
        fields = request.REQUEST.get('fl', None)
        res_format = request.REQUEST.get('format', None)
        if not res_format:
            accept_list = None
            if 'HTTP_ACCEPT' in request.environ:
                try:
                    accept_list = conneg_parse(request.environ['HTTP_ACCEPT'])
                except:
                    accept_list= [MT("text", "html")]
            if not accept_list:
                accept_list= [MT("text", "html")]
            mimetype = accept_list.pop(0)
            while(mimetype):
                if str(mimetype).lower() in ["text/html", "text/xhtml"]:
                    res_format = 'html'
                    break
                elif str(mimetype).lower() in ["text/plain", "application/json"]:
                    res_format = 'json'
                    break
                elif str(mimetype).lower() in ["text/xml"]:
                    res_format = 'xml'
                    break
                elif str(mimetype).lower() in ["text/csv"]:
                    res_format = 'csv'
                    break
                try:
                    mimetype = accept_list.pop(0)
                except IndexError:
                    mimetype = None
            # Whoops - nothing satisfies - return text/plain
            if not res_format:
                res_format = 'html'

        context['sort'] = 'score desc'
        # Lock down the sort parameter.
        if sort and sort in  context['sort_options']:
             context['sort'] = sort
             context['sort_text'] =  context['sort_options'][ context['sort']]
        
        context['chosen_fields'] = []
        context['chosen_fields'].extend( context['search_fields'])

        if fields:
            fields = fields.split(',')
        if fields and type(fields).__name__ == 'list':
            fields = [x.strip() for x in fields]
            for fld in fields:
                if fld in context['all_fields'] and not fld in context['chosen_fields']:
                    context['chosen_fields'].append(fld)

        for fld in additional_fields:
            if not fld in context['chosen_fields']:
                context['chosen_fields'].append(fld)

        context['fields_to_facet'] = []
        context['fields_to_facet'].extend(context['facetable_fields'])

        context['facet_limit'] = 10

        context['chosen_facets'] = {}
        
        query_filter = ""
        
        #Setup to capture all the url parameters needed to regenerate this search
        context['search'] = {}
        filter_url = ""
        
        for field in context['all_fields']:
            if request.REQUEST.get("filter"+field, None):
                multi = request.REQUEST.getall("filter"+field)
                context['chosen_facets'][field] = []
                #search["filter"+field] = ""
                for m in multi:
                    try:
                        m = unquote(m)
                    except:
                        pass
                    m = m.strip()
                    m = m.strip('"')
                    context['chosen_facets'][field].append(m)
                    query_filter += ' AND %s:"%s"'%(field, m)
                    try:
                        filter_url += '&filter%s=%s'%(field, quote('"%s"'%m))
                    except:
                        filter_url += '&filter%s=%s'%(field, '"%s"'%m)
                #if field in fields_to_facet:
                #    del fields_to_facet[field]
        
        for field in context['chosen_facets']:
            if field not in context['chosen_fields']:
               context[' chosen_fields'].append(field)

        context['truncate'] = 450
        context['start'] = 0
        context['rows'] = 25
        
        # Parse/Validate search controls
        if truncate:
            try:
                context['truncate'] = int(truncate)
            except ValueError:
                pass
            if context['truncate'] < 10:
                context['truncate'] = 10
            if context['truncate'] > 1000:
                context['truncate'] = 1000
             
        if start:
            try:
                context['start'] = int(start)
            except ValueError:
                pass
            if context['start'] < 0:
                context['start'] = 0

        if rows:
            try:
                context['rows'] = int(rows)
            except ValueError:
                pass
        if context['rows'] < 5:
            context['rows'] = 5
        elif context['rows'] > 5000:
            context['rows']=5000
            
        #search['rows'] = rows
        context['search']['truncate'] = context['truncate']
        context['search']['type'] = context['typ']
        #search['start'] = start
        #search['sort'] = sort
        #if q:
        #    search['q'] = q.encode('utf-8')
        solr_params = {}
        
        if context['q']:
            if context['typ'] and 'silo' in context['typ']:
                solr_params['q'] = context['q'].encode('utf-8')+query_filter+" AND type:silo"
            elif context['typ'] and 'dataset' in context['typ']:
                solr_params['q'] = context['q'].encode('utf-8')+query_filter+" AND type:dataset"
            elif context['typ'] and 'item' in context['typ'] and context['q'] != "*:*":
                #solr_params['q'] = """aggregatedResource:"%s" %s"""%(q.encode('utf-8'),query_filter)
                solr_params['q'] = """filename:"%s" %s"""%(context['q'].encode('utf-8'),query_filter)
            else:
                solr_params['q'] = context['q'].encode('utf-8')+query_filter  

            if res_format in ['json', 'xml', 'python', 'php']:
                solr_params['wt'] = res_format
            else:
                solr_params['wt'] = 'json'

            solr_params['fl'] = ','.join(context['chosen_fields'])
            solr_params['rows'] = context['rows']
            solr_params['start'] = context['start']

            if context['sort']:
                solr_params['sort'] = context['sort']
                 
            if context['fields_to_facet']:
                solr_params['facet'] = 'true'
                solr_params['facet.limit'] = context['facet_limit']
                solr_params['facet.mincount'] = 1
                solr_params['facet.field'] = []
                for facet in context['fields_to_facet']:
                    solr_params['facet.field'].append(facet)

            solr_response = None 
            try:
                solr_conn = settings.getSolrConnection()
                solr_response = solr_conn.raw_query(**solr_params)
                #print solr_response
            except:
                pass

            context['add_finder_facet'] =  u"%ssearch/detailed?q=%s&" % (settings.get("main:granary.uri_root"), context['q'].encode('utf-8'))
                     
            context['add_finder_facet'] = context['add_finder_facet']+ urlencode(context['search']) + filter_url
            
            context['add_facet'] = u"%ssearch/detailed?q=%s&" % ('/', context['q'].encode('utf-8'))
            context['add_facet'] = context['add_facet'] + urlencode(context['search']) + filter_url
            context['src'] = settings.get("main:granary.uri_root")
            if not solr_response:
                # conneg return
                #response.status_int = 200
                #response.status = "200 OK"
                if res_format == "html":
                    context['numFound'] = 0
                    context['message']= 'Sorry, either that search "%s" resulted in no matches, or the search service is not functional.' % context['q']
                    #return render('/search.html')
                    return render_to_response('search.html',context,context_instance=RequestContext(request))
 
                elif res_format == 'xml':
                    #response.headers['Content-Type'] = 'application/xml'
                    #response.charset = 'utf8'
                    context['atom'] = {}
                    #return render('/atom_results.html')
                    #c = RequestContext(request, context)
                    return render(request, 'atom_results.html',context,content_type="application/xml")
                elif res_format == 'json':
                    #esponse.headers['Content-Type'] = 'application/json'
                    #response.charset = 'utf8'
                    #return {}
                    return render(request,context,content_type="application/json")                   
                else:
                    #response.headers['Content-Type'] = 'application/text'
                    #response.charset = 'utf8'
                    return render(request,solr_response,content_type="application/text")
                    #return solr_response
        
            #response.status_int = 200
           # response.status = "200 OK"

            if res_format == 'xml':
                #response.headers['Content-Type'] = 'application/xml'
                #response.charset = 'utf8'
                context['atom'] = solr_response
                #return render('/atom_results.html')
                return render_to_response(request,'atom_results.html',context,content_type="application/xml")
            elif res_format == 'json':
                #response.headers['Content-Type'] = 'application/json'
                #response.charset = 'utf8'
                return render_to_response(request,solr_response,content_type="application/json")
                #return solr_response
            elif res_format in ['csv', 'python', 'php']:
                #response.headers['Content-Type'] = 'application/text'
                #response.charset = 'utf8'
                return render_to_response(request,solr_response,content_type="application/text")
            #return solr_response
                
            search = json.loads(solr_response)
                
            numFound = search['response'].get('numFound',None)
            
            context['numFound'] = 0
            context['permissible_offsets'] = []
            
            context['pages_to_show'] = 5
            
            try:
                context['numFound'] = int(numFound)
                remainder = context['numFound'] % context['rows']
                if remainder > 0:
                    context['lastPage'] = context['numFound'] - remainder
                else:
                    context['lastPage'] = context['numFound'] -context['rows']
                
                if context['numFound'] > context['rows']:
                    offset_start = context['start'] - ( (context['pages_to_show']/2) * context['rows'] )
                    if offset_start < 0:
                        offset_start = 0
                    
                    offset_end = offset_start + (context['pages_to_show'] * context['rows'])
                    offset_start = 0
                    
                    context['permissible_offsets'] = list( xrange( offset_start, offset_end, context['rows']) )
            except ValueError:
                pass

            context['docs'] = search['response'].get('docs',None)
        
            if context['fields_to_facet']:
                context['returned_facets'] = {}
                for facet in search['facet_counts']['facet_fields']:       
                    facet_list = search['facet_counts']['facet_fields'][facet]
                    keys = facet_list[::2]
                    values = facet_list[1::2]
                    context['returned_facets'][facet] = []
                    for index in range(len(keys)):
                        context['returned_facets'][facet].append((keys[index],values[index]))

            return render_to_response('search.html',context,context_instance=RequestContext(request))



def advanced(self):

        context['q'] = "*:*"
        context['typ'] = 'all'

        # Search controls
        format = 'html'
        context['sort'] = 'score desc'
        context['sort_text'] = context['sort_options'][context['sort']]
        
        context['chosen_fields'] = []
        context['chosen_fields'].extend(context['search_fields'])

        context['fields_to_facet'] = []
        context['fields_to_facet.extend'](context['facetable_fields'])

        context['facet_limit'] = 10

        context['chosen_facets'] = {}
        
        query_filter = ""
        
        #Setup to capture all the url parameters needed to regenerate this search
        context['search'] = {}
        filter_url = ""
        
        context['truncate'] = 450
        context['start'] = 0
        context['rows'] = 25
        context['search']['truncate'] = context['truncate']
        context['search']['type'] = context['typ']

        solr_params = {}
        solr_conn = None
        if context['q']:
            solr_params['q'] = context['q'].encode('utf-8')+query_filter  
            solr_params['wt'] = 'json'
            solr_params['fl'] = ','.join(context['chosen_fields'])
            solr_params['rows'] = context['rows']
            solr_params['start'] = context['start']
            if context['sort']:
                solr_params['sort'] = context['sort']                
            if context['fields_to_facet']:
                solr_params['facet'] = 'true'
                solr_params['facet.limit'] = context['facet_limit']
                solr_params['facet.mincount'] = 1
                solr_params['facet.field'] = []
                for facet in context['fields_to_facet']:
                    solr_params['facet.field'].append(facet)
            try:
                #solr_response = ag.solr.raw_query(**solr_params)
                solr_conn = settings.getSolrConnection()
                solr_response = solr_conn.raw_query(**solr_params)
            except:
                solr_response = None
        

            context['add_facet'] =  u"%ssearch/detailed?q=%s&" % (settings.get("main:granary.uri_root"), context['q'].encode('utf-8'))
            context['add_facet'] = context['add_facet'] + urlencode(context['search']) + filter_url
 
            if not solr_response:
                # FAIL - do something here:
                context['message'] = 'Sorry, either that search "%s" resulted in no matches, or the search service is not functional.' % context['q']
                h.redirect_to(controller='/search', action='index')
        
            search = json.loads(solr_response)
                
            numFound = search['response'].get('numFound',None)
            try:
                context['numFound'] = int(numFound)
            except:
                context['numFound'] = 0
            context['docs'] = search['response'].get('docs',None)
        
            if context['fields_to_facet']:
                context['returned_facets'] = {}
                for facet in search['facet_counts']['facet_fields']:       
                    facet_list = search['facet_counts']['facet_fields'][facet]
                    keys = facet_list[::2]
                    values = facet_list[1::2]
                    context['returned_facets'][facet] = []
                    for index in range(len(keys)):
                        context['returned_facets'][facet].append((keys[index],values[index]))
        return render_to_response('search_advanced.html',context,context_instance=RequestContext(request))
        #return render('/search_advanced.html')
