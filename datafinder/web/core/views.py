from djangomako.shortcuts import render_to_response, render_to_string
from django.shortcuts import redirect
from django.conf import settings
from datafinder.config import settings
from datafinder.lib.HTTP_request import HTTPRequest
from django.template import RequestContext
import logging, os, json
from datafinder.lib.search_term import term_list
from datetime import  date, timedelta
from datafinder.lib.SolrQuery import SolrQuery

def home(request):

    context = {}
    
    end = date.today()
    start = end-timedelta(days=7)
    #SolrQuery(self, query_filter = "" , q = "*:*" , req_format="json")
    q1 = "*:*"
    solr_query = SolrQuery(q=q1)
    context['numFound'] = solr_query.get_NumRecordsFound()
    
    q2 = "timestamp:["+ str(start) + "T00:00:00Z" + " TO "+ str(end) + "T00:00:00Z" + "]"
    solr_query = SolrQuery(q=q2)
    
    context['numFoundThisWeek'] = solr_query.get_NumRecordsFound()
    
    return render_to_response('home.html',context, context_instance=RequestContext(request))
 

def browse(request):
    context = {}
    return render_to_response('browse.html',context, context_instance=RequestContext(request))

def accessibility(request):
    context = {}
    return render_to_response('accessibility.html',context, context_instance=RequestContext(request))

def privacy(request):
    context = {}
    return render_to_response('privacy.html',context, context_instance=RequestContext(request))

def termsconditions(request):
    context = {}
    return render_to_response('terms-conditions.html',context, context_instance=RequestContext(request))

def about(request):
    context = {}
    return render_to_response('about.html',context, context_instance=RequestContext(request))

def contact(request):
    context = {}
    return render_to_response('contact.html',context, context_instance=RequestContext(request))

def help(request):
    context = {}
    return render_to_response('help.html',context, context_instance=RequestContext(request))


def cookies(request):
    context = {}
    return render_to_response('cookies.html',context, context_instance=RequestContext(request))

def myrecords(request):
    context={}
    try:
        # A user needs to be authenticated  to be able to view my records page in the DataFinder                          
        # Test if the user is now a university authenticated user
        if 'DF_USER_SSO_ID' not in request.session:                          
                return redirect("/login?redirectPath=myrecords")    
    
        http_method = request.environ['REQUEST_METHOD'] 
        
        #if http_method == "GET":            
                #user_name = settings.get("main:granary.uri_root_name") 
                #password = settings.get("main:granary.uri_root_pass") 
                #datastore = HTTPRequest(endpointhost=settings.get("main:granary.host"))       
                #datastore.setRequestUserPass(endpointuser=user_name, endpointpass=password)
                #(resp,respdata) = datastore.doHTTP_GET( resource="/DataFinder/datasets/" + identifier +"/")
                
        #        context = { 
#            'DF_VERSION':settings.DF_VERSION,
#            'STATIC_URL': settings.STATIC_URL,
#            'silo_name':"",
#            'ident' : "",
#            'id':"",
#            'path' :"",
#            'q':"",
#            'typ':"",
#            'docs':"",
#            }
        context = {}
        context['all_fields'] = term_list().get_all_search_fields()
        context['field_names'] = term_list().get_search_field_dictionary()
        context['facetable_fields'] = term_list().get_all_facet_fields()
        context['types'] = term_list().get_type_field_dictionary()
        context['search_fields'] = ['silo', 'id', 'title', 'uuid', 'embargoStatus', 'embargoedUntilDate', 'currentVersion', 'doi', 'publicationDate', 'abstract', 'description', 'creator', 'isVersionOf', 'isPartOf', 'subject', 'type']
        context['sort_options'] = {'score desc':'Relevance',  'publicationDate desc':'Date (Latest to oldest)','publicationDate asc':'Date (Oldest to Latest)','silo asc':'Silo A to Z','silo desc':'Silo Z to A'}

        #if query:
        #    context['q'] = query
        #else:        
        #    context['q'] = request.REQUEST.get('q',None)
        #try:
        #    context['web_auth_user']
            #context['q'] = unquote(context['q'])
        #except:
        #    pass
        session_user =  request.session['DF_USER_SSO_ID']
        
        context['typ'] = 'all'
        if request.REQUEST.get("type",None):
            context['typ'] = request.REQUEST.get("type",None)

        if not context['q'] or context['q'] == '*' or context['q'] == "":
            context['q'] = "*:*"
 
        # Search controls
        #truncate = request.REQUEST.get('truncate', None)
        #start = request.REQUEST.get('start', None)
        #rows = request.REQUEST.get('rows', None)
        #sort = request.REQUEST.get('sort', None)
        #fields = request.REQUEST.get('fl', None)
        #res_format = request.REQUEST.get('format', None)
        
#        if not res_format:
#            accept_list = None
#            if 'HTTP_ACCEPT' in request.environ:
#                try:
#                    accept_list = conneg_parse(request.environ['HTTP_ACCEPT'])
#                except:
#                    accept_list= [MT("text", "html")]
#            if not accept_list:
#                accept_list= [MT("text", "html")]
#            mimetype = accept_list.pop(0)
#            while(mimetype):
#                if str(mimetype).lower() in ["text/html", "text/xhtml"]:
#                    res_format = 'html'
#                    break
#                elif str(mimetype).lower() in ["text/plain", "application/json"]:
#                    res_format = 'json'
#                    break
#                elif str(mimetype).lower() in ["text/xml"]:
#                    res_format = 'xml'
#                    break
#                elif str(mimetype).lower() in ["text/csv"]:
#                    res_format = 'csv'
#                    break
#                try:
#                    mimetype = accept_list.pop(0)
#                except IndexError:
#                    mimetype = None
#            # Whoops - nothing satisfies - return text/plain
#            if not res_format:
#                res_format = 'html'
                
        res_format = 'json'
        context['sort'] = 'score desc'
        # Lock down the sort parameter.
        if sort and sort in  context['sort_options']:
             context['sort'] = sort
             context['sort_text'] =  context['sort_options'][ context['sort']]
        
        context['chosen_fields'] = []
        context['chosen_fields'].extend( context['search_fields'])

#        if fields:
#            fields = fields.split(',')
#        if fields and type(fields).__name__ == 'list':
#            fields = [x.strip() for x in fields]
#            for fld in fields:
#                if fld in context['all_fields'] and not fld in context['chosen_fields']:
#                    context['chosen_fields'].append(fld)
#
#        for fld in additional_fields:
#            if not fld in context['chosen_fields']:
#                context['chosen_fields'].append(fld)

        context['fields_to_facet'] = []
        context['fields_to_facet'].extend(context['facetable_fields'])

        context['facet_limit'] = 10

        context['chosen_facets'] = {}
        
        query_filter = ""
        
        #Setup to capture all the url parameters needed to regenerate this search
        context['search'] = {}
        filter_url = ""
        
#        for field in context['all_fields']:
#            if request.REQUEST.get("filter"+field, None):
#                multi = request.REQUEST.getall("filter"+field)
#                context['chosen_facets'][field] = []
#                #search["filter"+field] = ""
#                for m in multi:
#                    try:
#                        m = unquote(m)
#                    except:
#                        pass
#                    m = m.strip()
#                    m = m.strip('"')
#                    context['chosen_facets'][field].append(m)
#                    query_filter += ' AND %s:"%s"'%(field, m)
#                    try:
#                        filter_url += '&filter%s=%s'%(field, quote('"%s"'%m))
#                    except:
#                        filter_url += '&filter%s=%s'%(field, '"%s"'%m)
#                #if field in fields_to_facet:
#                #    del fields_to_facet[field]
#        
#        for field in context['chosen_facets']:
#            if field not in context['chosen_fields']:
#               context[' chosen_fields'].append(field)

        context['truncate'] = 450
        context['start'] = 0
        context['rows'] = 25
        
        # Parse/Validate search controls
#        if truncate:
#            try:
#                context['truncate'] = int(truncate)
#            except ValueError:
#                pass
#            if context['truncate'] < 10:
#                context['truncate'] = 10
#            if context['truncate'] > 1000:
#                context['truncate'] = 1000
#             
#        if start:
#            try:
#                context['start'] = int(start)
#            except ValueError:
#                pass
#            if context['start'] < 0:
#                context['start'] = 0
#
#        if rows:
#            try:
#                context['rows'] = int(rows)
#            except ValueError:
#                pass
#        if context['rows'] < 5:
#            context['rows'] = 5
#        elif context['rows'] > 5000:
#            context['rows']=5000
            
        #search['rows'] = rows
        #context['search']['truncate'] = context['truncate']
        #context['search']['type'] = context['typ']
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
                print "before solr connection :"
                solr_conn, b = settings.getSolrConnection()
                solr_response = solr_conn.raw_query(**solr_params)
                print "solr response :"
                print solr_response
            except:
                print "in exception"
                pass
            print "after try block"
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
#                    return render_to_response('search.html',context,context_instance=RequestContext(request))                   
                    return render_to_response('searchresults-mockup.html',context, context_instance=RequestContext(request))
 
                elif res_format == 'xml':
                    #response.headers['Content-Type'] = 'application/xml'
                    #response.charset = 'utf8'
                    context['atom'] = {}
                    #return render('/atom_results.html')
                    #c = RequestContext(request, context)
                    #return render(request, 'atom_results.html',context,content_type="application/xml")
                    t = loader.get_template('atom_results.html')
                    c = RequestContext(request, context)
                    return HttpResponse(t.render(c),  content_type="application/xml")
                elif res_format == 'json':
                    #esponse.headers['Content-Type'] = 'application/json'
                    #response.charset = 'utf8'
                    #return {}
                    #return render(request,context,content_type="application/json")   
                    return HttpResponse(solr_response, mimetype='application/json')                
                else:
                    #response.headers['Content-Type'] = 'application/text'
                    #response.charset = 'utf8'
                    #return render(request,solr_response,content_type="application/text")
                    return HttpResponse(solr_response, mimetype='application/text') 
                    #return solr_response
        
            #response.status_int = 200
            # response.status = "200 OK"

            if res_format == 'xml':
                #response.headers['Content-Type'] = 'application/xml'
                #response.charset = 'utf8'
                context['atom'] = solr_response
                #return render('/atom_results.html')
                #return render_to_response(request,'atom_results.html',context,content_type="application/xml")
                t = loader.get_template('atom_results.html')
                c = RequestContext(request, context)
                return HttpResponse(t.render(c),  content_type="application/xml")
            elif res_format == 'json':
                #response.headers['Content-Type'] = 'application/json'
                #response.charset = 'utf8'
                #return render_to_response(request,solr_response,content_type="application/json")
                #return solr_response
                return HttpResponse(solr_response, mimetype='application/json')   
            elif res_format in ['csv', 'python', 'php']:
                #response.headers['Content-Type'] = 'application/text'
                #response.charset = 'utf8'
                #return render_to_response(request,solr_response,content_type="application/text")
                return HttpResponse(solr_response, mimetype='application/text') 
            #return solr_response
                
            search = json.loads(solr_response)
            context['search'] = search
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

#            return render_to_response('search.html',context,context_instance=RequestContext(request))
            return render_to_response('searchresults-mockup.html',context, context_instance=RequestContext(request))
 
    except Exception, e:
        raise
     
    return render_to_response('myrecords.html',context, context_instance=RequestContext(request))

