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
                
                context["data_description"]=request.GET['data_description']
                context["data_process"]=request.GET['data_process']
                context["project_desc"]=request.GET['project_desc']
                context["project_website"]=request.GET['project_website']
                context["subject_areas"]=request.GET['subject_areas']
                context["record_keywords"]=request.GET['record_keywords']
                context["main_language"]=request.GET['main_language']
                context["author_firstname_1"]=request.GET['author_firstname_1']
                context["author_lastname_1"]=request.GET['author_lastname_1']        
                context["author_role_1"]=request.GET['author_role_1']
                context["author_affiliation_1"]=request.GET['author_affiliation_1']
                context["record_contact"]=request.GET['record_contact']  
                context["data-format"]=request.GET['data-format']
                if context["data-format"] == "yes":
                    context["digital_location"]=request.GET['digital_location']
                    context["digital_resource_type"]=request.GET['digital_resource_type']      
                    context["digital_filesize"]=request.GET['digital_filesize']
                    context["digital_format"]=request.GET['digital_format']
                    context["digital_version"]=request.GET['digital_version']
                    context["digital_publisher"]=request.GET['digital_publisher']
                    context["digital_publish_year"]=request.GET['digital_publish_year']
                    context["whereis_non_digital"]=request.GET['whereis_non_digital']
                if context["data-format"] == "no":                    
                    context["non_digital_format"]=request.GET['non_digital_format']
                    context["non_digital_publisher"]=request.GET['non_digital_publisher']
                    context["non_digital_publish_year"]=request.GET['non_digital_publish_year']
                context["funded_research"]=request.GET['funded_research']
                if context["funded_research"] == "no":
                    context["funding_agency"]=request.GET['funding_agency']
                    context["grant_number"]=request.GET['grant_number']
                context["data_management_plan_location"]=request.GET['data_management_plan_location']
                context["publication_relationship_of_data_1"]=request.GET['publication_relationship_of_data_1']
                context["related_publication_url_1"]=request.GET['related_publication_url_1']
                context["dataset_relationship_of_data_1"]=request.GET['dataset_relationship_of_data_1']
                context["dataset_related_url_1"]=request.GET['dataset_related_url_1']
                context["terms_and_conditions"]=request.GET['terms_and_conditions']
                context["data_standard_licence"]=request.GET['data_standard_licence']
                context["embargo-options"]=request.GET['embargo-options']
                context["subject_specific_metadata_file"]=request.GET['subject_specific_metadata_file']
                context["xml_schema_type"]=request.GET['xml_schema_type']
                return render_to_response('contribute.html', context, context_instance=RequestContext(request))
                                        
   except Exception, e:
        raise
