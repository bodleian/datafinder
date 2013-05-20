from djangomako.shortcuts import render_to_response, render_to_string 
from django.conf import settings
from django.shortcuts import redirect
from django.template import RequestContext
import logging,os, sys
import rdflib
from rdflib import Literal
import datafinder.util.serializers
from datafinder.namespaces import OXDS, DCTERMS, RDF, FOAF, FUND, bind_namespaces, FUND
from pwd import  getpwnam 
sys.path.append("../..")
from django.http import HttpResponse
from datafinder.lib.DF_Auth_Session import DFAuthSession
from datafinder.config import settings
from datafinder.lib.HTTP_request import HTTPRequest
from datafinder.lib import SparqlQueryTestCase
from datafinder.lib.CUD_request import CUDRequest
import json as simplejson
import xml.etree.ElementTree as ET
import xml
from datafinder.config import settings
from datafinder.lib.broadcast import BroadcastToRedis

try: 
    import simplejson as json
except ImportError: 
    import json

def recordsmockup(request):
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

    return render_to_response('records_mockup.html',context, context_instance=RequestContext(request))
    
def contribute(request):
   try:
        # A user needs to be authenticated  to be able to contribute a record  the DataFinder                          
        # Test if the user is now a university authenticated user
        if 'DF_USER_SSO_ID' not in request.session:                          
            return redirect("/login?redirectPath=contribute")    
        
        context = {}
        literals = {}
        resources = {}
        project = {}
        person = {}
                
        if request.GET.has_key('message'):    
            context["message"]=request.GET['message']
        if request.GET.has_key('status'):    
            context["status"]=request.GET['status']

        http_method = request.environ['REQUEST_METHOD'] 
        
        if http_method == "GET":      
            return render_to_response('contribute.html', context, context_instance=RequestContext(request))  
        elif http_method == "POST":             
            if request.POST.has_key('record_title'):
                             
                literals[DCTERMS['title']]=request.POST['record_title']
                literals[DCTERMS['alternative']]=request.POST['alt_title']
                #context["deposit_data_file_upload"]=request.POST['deposit_data_file_upload']
                #context["deposit_data_embargo_options"]=request.POST['deposit_data_embargo_options']
                #context["deposit_data_embrago_release_date"]=request.POST['deposit_data_embrago_release_date']
                #context["deposit_data_embargo_options_type"]=request.POST['deposit_data_embargo_options_type']
                #context["deposit_data_embargo_reason"]=request.POST['deposit_data_embargo_reason']
                
                literals[DCTERMS['description']]=request.POST['data_description']
                literals[OXDS['methodology']]=request.POST['data_process']
                
                project[DCTERMS['title']]=request.POST['project_desc']
                project[DCTERMS['URI']]=request.POST['project_website']
                 
                literals[DCTERMS['subject']]=request.POST['subject_areas']
                literals[DCTERMS['keywords']]=request.POST['record_keywords']
                literals[DCTERMS['language']]=request.POST['main_language']
                
                literals[DCTERMS['status']]='seeking_approval'
                
#               cud_authenticator = settings.get('main:cud_proxy.host')
#               cudReq = CUDRequest(cud_proxy_host=cud_authenticator, {'sso_username':request.session['DF_USER_SSO_ID']})
                literals[OXDS['depositor']] = request.session['DF_USER_SSO_ID']
                #context["author_firstname_1"]=request.GET['author_firstname_1']
                
                #context["author_lastname_1"]=request.GET['author_lastname_1']        
                #context["author_role_1"]=request.GET['author_role_1']
                #context["author_affiliation_1"]=request.GET['author_affiliation_1']
                #context["record_contact"]=request.GET['record_contact']  
                
                literals[OXDS['contact']] = request.POST['record_contact']
                literals[OXDS['isEmbargoed']] = 'False'
                if request.POST.has_key('data-format'):
                    literals[OXDS['isDigital']]=request.POST['data-format']
                if literals[OXDS['isDigital']] == "yes":
                    literals[OXDS['DataLocation']]=request.POST['digital_location']
                    literals[DCTERMS['type']]=request.POST['digital_resource_type']      
                    literals[OXDS['Filesize']]=request.POST['digital_filesize']
                    literals[DCTERMS['format']]=request.POST['digital_format']
                    literals[OXDS['currentversion']]=request.POST['digital_version']
                    context[DCTERMS['publisher']]=request.POST['digital_publisher']
                    #context["digital_publish_year"]=request.POST['digital_publish_year']
                    #context["whereis_non_digital"]=request.POST['whereis_non_digital']
                if literals[OXDS['isDigital']] == "no":                    
                    context[DCTERMS['format']]=request.POST['non_digital_format']
                    context[DCTERMS['publisher']]=request.POST['non_digital_publisher']
                    context[DCTERMS['issued']]=request.POST['non_digital_publish_year']
                
                funded_research = ''#request.POST['funded_research']
                if funded_research == "yes":
                    context[FUND['FundingBody']]=request.POST['funding_agency']
                    context[FUND['grantNumber']]=request.POST['grant_number']
                    
                     

                #context["data_management_plan_location"]=request.GET['data_management_plan_location']
                #context["publication_relationship_of_data_1"]=request.GET['publication_relationship_of_data_1']
                #context["related_publication_url_1"]=request.GET['related_publication_url_1']
                #context["dataset_relationship_of_data_1"]=request.GET['dataset_relationship_of_data_1']
                #context["dataset_related_url_1"]=request.GET['dataset_related_url_1']
                #context["terms_and_conditions"]=request.GET['terms_and_conditions']
                #context["data_standard_licence"]=request.GET['data_standard_licence']
                #context["embargo-options"]=request.GET['embargo-options']
                #context["subject_specific_metadata_file"]=request.GET['subject_specific_metadata_file']
                #context["xml_schema_type"]=request.GET['xml_schema_type']
                
                # Project RDF
                #projects_package = rdflib.URIRef(projects_path)
                
                
                projects_path = settings.get("main:granary.projects_path")
        
                projects_manifest_filename = os.path.join(projects_path, 'projects.rdf')
                projects_manifest = bind_namespaces(rdflib.ConjunctiveGraph())
#              
                try:
                    with open(projects_manifest_filename, 'r') as f:
                        projects_manifest.parse(f, base=projects_manifest_filename)
                except IOError, e:
                    pass
                
                
                for key, value in project.items():
                    # Will raise UniquenessError if >1 value returned, must be one or None
                    if projects_manifest.value(None, DCTERMS['title'], Literal(value)) == None:                        
                        projects_manifest.add((FUND[project[DCTERMS['title']]], key, Literal(value)))
                        projects_manifest.add((FUND[project[DCTERMS['title']]], key, Literal(value)))
                    
                with open(projects_manifest_filename, 'w') as f:
                    projects_manifest.serialize(f, 'better-pretty-xml', base=projects_manifest_filename)
                os.chown(projects_manifest_filename,  getpwnam('www-data').pw_uid, getpwnam('www-data').pw_gid)
                resources[FUND['project']] = FUND[project[DCTERMS['title']]]
                
                # Record Manifest RDF
                records_path = settings.get("main:granary.records_path")
                records_package = rdflib.URIRef(records_path)
                manifest_name = 'df_manifest_'+literals[DCTERMS['title']] +'.rdf'
                manifest_filename = os.path.join(records_path, manifest_name)
                main_manifest_filename = os.path.join(records_path, 'manifest.rdf')
                manifest = bind_namespaces(rdflib.ConjunctiveGraph())
                #try:
                #    with open(manifest_filename, 'w') as f:
                #        manifest.parse(f, base=manifest_filename)
                #except IOError, e:
                #    pass
                
                for key, value in literals.items():
                    manifest.add((OXDS[literals[DCTERMS['title']]], key, Literal(value)))
                
                for key, res_uri in resources.items():
                    manifest.add(((OXDS[literals[DCTERMS['title']]], key, res_uri)))
                    
                with open(manifest_filename, 'w') as f:
                    manifest.serialize(f, 'better-pretty-xml', base=manifest_filename)
                                
#                try:
#                    with open(main_manifest_filename, 'w') as f:
#                        manifest.parse(f, base=main_manifest_filename)
               
#                except IOError, e:
#                    pass
                                
                user_name = settings.get("main:granary.uri_root_name") 
                password = settings.get("main:granary.uri_root_pass") 
                datastore = HTTPRequest(endpointhost=settings.get("main:granary.host"))       
                datastore.setRequestUserPass(endpointuser=user_name, endpointpass=password)
                identifier = literals[DCTERMS['title']]
                #(reqtype, reqdata) = SparqlQueryTestCase.encode_multipart_formdata([], [])
                # Create a dataset
                #(resp,respdata) = datastore.doHTTP_POST(reqdata, reqtype, resource="/DataFinder/datasets/" + identifier)

                #Submit the df_manefest as a file
                fields=[]
                df_namifest = open(manifest_filename).read()               
                files =  [("file", manifest_name, df_namifest, "application/rdf+xml")]            
                (reqtype, reqdata) = SparqlQueryTestCase.encode_multipart_formdata(fields, files)                
                (resp,respdata) = datastore.doHTTP_POST(reqdata, reqtype, resource="/DataFinder/datasets/" + identifier +"/")
                
                silo = settings.get("main:mainsilo")
                #solr_conn, b = settings.getSolrConnection()
                b = BroadcastToRedis('localhost', 'silochanges')
                b.creation(silo, identifier, ident=request.session['DF_USER_SSO_ID'])
                
                #Submit the main manifest file which as the see also
                fields=[]       
                main_manifest = open(main_manifest_filename).read()         
                files =  [("file", "manifest.rdf", main_manifest, "application/rdf+xml")]            
                (reqtype, reqdata) = SparqlQueryTestCase.encode_multipart_formdata(fields, files)                
                (resp,respdata) = datastore.doHTTP_POST(reqdata, reqtype, resource="/DataFinder/datasets/" + identifier +"/")

                os.chown(manifest_filename, getpwnam('www-data').pw_uid, getpwnam('www-data').pw_gid)
                return render_to_response('contribute.html', context, context_instance=RequestContext(request))                                       
   except Exception, e:
        raise
    

def projects(request):
   try:
        # A user needs to be authenticated  to be able to contribute a record  the DataFinder                          
        # Test if the user is now a university authenticated user
        if 'DF_USER_SSO_ID' not in request.session:                          
            return redirect("/login?redirectPath=contribute")    
        
        #context = {}
        projects = []
    
        projects_path = settings.get("main:granary.projects_path")
        
        projects_manifest_filename = os.path.join(projects_path, 'projects.rdf')
        projects_manifest = bind_namespaces(rdflib.ConjunctiveGraph())
#              
        try:
            with open(projects_manifest_filename, 'r') as f:
                projects_manifest.parse(f, base=projects_manifest_filename)
        except IOError, e:
            pass
                
        #if request.GET.has_key('message'):    
        #    context["message"]=request.GET['message']
        #if request.GET.has_key('status'):    
        #    context["status"]=request.GET['status']

        http_method = request.environ['REQUEST_METHOD'] 
        
        if http_method == "POST" or http_method == "GET":     
   #projects[o1] =projects_manifest.value(s1,DCTERMS['URI'],None)

            for s1,p1,o1 in projects_manifest.triples((None,DCTERMS['title'],None)):
                                       projects.append(o1)
            #context['projects'] = projects
            
            return HttpResponse(json.dumps(projects), mimetype="application/json")
            #return render_to_response('contribute.html', context, context_instance=RequestContext(request))  
       # elif http_method == "POST":             
       #     return render_to_response('contribute.html', context, context_instance=RequestContext(request))                                       
   except Exception, e:
        raise
    


def languages(request):
   try:
        # A user needs to be authenticated  to be able to contribute a record  the DataFinder                          
        # Test if the user is now a university authenticated user
        if 'DF_USER_SSO_ID' not in request.session:                          
            return redirect("/login?redirectPath=contribute")    
        
        #context = {}
        languages = []
        tmp=[]
        languages_xml_file_path = settings.get("main:granary.languages_path")
        
        languages_xml_filename = os.path.join(languages_xml_file_path, 'languages-iso-639.xml')
      
        tree = ET.parse(languages_xml_filename)
        for elem in tree.iter():
            if request.GET['lang'].lower() in elem.text.lower():
                if elem.text[:len(request.GET['lang'])].lower() == request.GET['lang'].lower() :
                    languages.append(elem.text)
                else:
                    tmp.append(elem.text)
        languages.sort();
        tmp.sort();

        languages = languages + tmp;
        
        return HttpResponse(json.dumps(languages), mimetype="application/json")
            #return render_to_response('contribute.html', context, context_instance=RequestContext(request))  
       # elif http_method == "POST":             
       #     return render_to_response('contribute.html', context, context_instance=RequestContext(request))                                       
   except Exception, e:
        raise
        
        
def peopleFromCUD(request):
   try:
        # A user needs to be authenticated  to be able to contribute a record  the DataFinder                          
        # Test if the user is now a university authenticated user
        if 'DF_USER_SSO_ID' not in request.session:                          
            return redirect("/login?redirectPath=contribute")    

        http_method = request.environ['REQUEST_METHOD'] 
        context = {}
        if http_method == "POST":
            cud_authenticator = settings.get('main:cud_proxy.host')
            data_filter = {}
            if request.POST.has_key('lastname') and request.POST['lastname'] != "": 
                data_filter['lastname']= request.POST['lastname']
            if request.POST.has_key('firstname') and request.POST['firstname'] != "":
                data_filter['firstname']= request.POST['firstname']
            if request.POST.has_key('middlename') and request.POST['middlename'] != "":
                data_filter['middlename']= request.POST['middlename']
            if request.POST.has_key('email') and request.POST['email'] != "":
                data_filter['oxford_email']= request.POST['email']

            cudReq = CUDRequest(cud_proxy_host=cud_authenticator,filter=data_filter)
            

            context["firstname"]  =  sorted(set(cudReq.get_filter_values('firstname')))
            #str(cudReq.get_filter_values('sso_username'))
            context["lastname"]  = sorted(set(cudReq.get_filter_values('lastname')))
            context["middlename"]  = sorted(set(cudReq.get_filter_values('middlename')))
            context["email"]  = sorted(set(cudReq.get_filter_values('oxford_email')))            
            
        return HttpResponse(json.dumps(context), mimetype="application/json")
            #return render_to_response('contribute.html', context, context_instance=RequestContext(request))  
       # elif http_method == "POST":             
       #     return render_to_response('contribute.html', context, context_instance=RequestContext(request))                                       
   except Exception, e:
        raise
        

    
