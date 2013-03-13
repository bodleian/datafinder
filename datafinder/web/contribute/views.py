from djangomako.shortcuts import render_to_response, render_to_string 
from django.conf import settings
from django.shortcuts import redirect
from django.template import RequestContext
import logging,os, sys

sys.path.append("../..")

from datafinder.lib.DF_Auth_Session import DFAuthSession
from datafinder.config import settings

def contribute(request):
   try:
        # A user needs to be authenticated  to be able to contribute a record  the DataFinder                          
        # Test if the user is now a university authenticated user
        if 'DF_USER_SSO_ID' not in request.session:                          
            return redirect("/login?redirectPath=contribute")    
        context = {}
        
        if request.GET.has_key('message'):    
            context["message"]=request.GET['message']
        if request.GET.has_key('status'):    
            context["status"]=request.GET['status']
            
        http_method = request.environ['REQUEST_METHOD'] 
        
        if http_method == "GET":         
            return render_to_response('contribute.html', context, context_instance=RequestContext(request))  
        elif http_method == "POST": 
            if request.POST.has_key('record_title'):
                context["record_title"]=request.GET['record_title']
                context["alt_title"]=request.GET['alt_title']
                context["deposit_data_file_upload"]=request.GET['deposit_data_file_upload']
                context["deposit_data_embargo_options"]=request.GET['deposit_data_embargo_options']
                context["deposit_data_embrago_release_date"]=request.GET['deposit_data_embrago_release_date']
                context["deposit_data_embargo_options_type"]=request.GET['deposit_data_embargo_options_type']
                context["deposit_data_embargo_reason"]=request.GET['deposit_data_embargo_reason']
                #context["alt_title"]=request.GET['alt_title']
                #context["alt_title"]=request.GET['alt_title']
                #context["alt_title"]=request.GET['alt_title']
                #context["alt_title"]=request.GET['alt_title']
                #context["alt_title"]=request.GET['alt_title']
                #context["alt_title"]=request.GET['alt_title']
                #context["alt_title"]=request.GET['alt_title']
                #context["alt_title"]=request.GET['alt_title']
                #context["alt_title"]=request.GET['alt_title']                
   except Exception, e:
        raise
