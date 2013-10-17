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
            
        status=""
        
        if request.GET.has_key('status'):
            status = request.GET['status']
   
        http_method = request.environ['REQUEST_METHOD'] 
        if http_method == "GET":                     
            if status == 'All' or status == "":
                 query = 'depositor:"' + request.session['DF_USER_SSO_ID'] + '"'                        
            else:   
                 query = 'depositor:"' + request.session['DF_USER_SSO_ID'] + '"' + ' AND ' 'status:"' + status + '"'             
                              
            solr_query = SolrQuery(q=query)
            context['solr_response'] = solr_query.get_solrresponse()
    except Exception, e:
        raise
     
    return render_to_response('myrecords.html',context, context_instance=RequestContext(request))

