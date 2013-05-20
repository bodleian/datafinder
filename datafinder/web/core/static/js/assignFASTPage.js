var $j=jQuery.noConflict();  //I like it clear which package I'm using, don't know why I use the $ at all.
//  note $j.dump(obj) is handy for debug, jquery.dump.js needed 


/*
    javascript in this file controls the html page demonstrating the autosubject functionality

*/

/*************************************************************************************/
/** 
 **  Most text here for easy updates
 **  
**/
/*************************************************************************************/
var documentTitle = "assignFAST";
var mastheadTitle = "<a href=\"http://experimental.worldcat.org/fast/assignfast/\">assignFAST</a>";
var mastheadSubTitle = "Assign FAST Subject Headings in a Single Step";
var exampleMastheadTitle = "assignFAST Simple Example for API"
var exampleMastheadSubTitle = "Assign FAST Subject Headings in a Single Step";
var searchBar = "assignFAST Demo";
var homeInfoAbout = "About"; //entry page only with message of day
var messageOfDay = "<h4>assignFAST Details</h4>\
                    <p>This is a demo of FAST Subject selection based on autosuggest technology.</p>\
                    <p>Start typing, and suggested See also and Authorized headings will appear.</p>\
						  <p>Selecting either type of heading will place the properly formatted Authorized heading in the box. The text will be highlighted already, ready for copying. </p>\
						  <p>The data is available as a Web Service, and the javascript can he easily \
						  added to a cataloging interface to allow easy selection of controlled FAST headings.\
						  In this way, even the cut and paste can be eliminated.  See the <a href=\"http://oclc.org/developer/services/assignfast\">API</a> on the OCLC Developers Network for details.</p>"
var TODO         = "<h4>TODO</h4>\
                    <ul>\
							 <li>NOTE- Add ?nocache after .xml when modifying in iGoogle</li>\
							 </ul>";
var addInfo         = "<h4>Additional Information</h4>\
						  <p>Need more features? Use the The full featured <a href=\"http://fast.oclc.org/searchfast/\" >searchFAST</a> interface.</p>\
						  <p>You can learn more about the FAST project by visiting the FAST project\
						   home page at: <a href=\"http://www.oclc.org/research/activities/fast/\">\
							http://www.oclc.org/research/activities/fast/</a></p>"; //only visible on entry page
var gadgetInfo      = "<h3 class=\"colhead\">OpenSocial Gadgets</h3>\
						  <p>These views are available as OpenSocial <a href=\"#\">gadgets</a> that can be added to the OCLC WorldShare Platform or other OpenSocial platforms. </p>\
						  <p>Common Format\
						  <p>http://experimental.worldcat.org/fast/assignfast/common.xml\
						  </p></p>\
						  <p>marcBreaker Format\
						  <p>http://experimental.worldcat.org/fast/assignfast/breaker.xml\
						  </p></p>\
						  <p>Connexion Format\
						  <p>http://experimental.worldcat.org/fast/assignfast/connexion.xml\
						  </p></p>"
var lastUpdate="The most recent update for FAST was 11/26/2012. The FAST database will be updated periodically. Our target is to update FAST at least twice each year.";
var projectTitle = mastheadTitle;
var comments = "<h4>For comments on assignFAST contact the <a href=\"http://www.oclc.org/research/feedback/form.asp?project=FAST\" target=\"_blank\" >FAST Team</a></h4>";


/**************************************************************************************/
/*              Set up and initialization */
/**************************************************************************************/
/*
initial setup - called from onLoad
  display settings
  attaches the autocomplete functions to the search boxes
*/

function setUpPage() {
   /*  Display text and other setup */
   
  document.title = documentTitle;
  // Use the ini file to set the main titles, etc.
  if(mastheadTitle != undefined)
      $j('#masthead h1').html(mastheadTitle);
  if(mastheadSubTitle != undefined)
      $j('#masthead h2').html(mastheadSubTitle);
  if(lastUpdate != undefined)
     $j('.foot-date').html(lastUpdate);  
  if(homeInfoAbout != undefined)
     $j('#homeInfo h3').html(homeInfoAbout);  
  if(projectTitle != undefined)
     $j('.projecttitle').html(projectTitle);  
  if(comments != undefined)
     $j('#feedback-form').html(comments);  
  if(searchBar != undefined)
    $j('#homeSearch h3').html(searchBar);  
  if(messageOfDay != undefined)
      $j('#messageOfDay').html(messageOfDay);
//  if(TODO != undefined)
//      $j('#todo').html(TODO);
  if(addInfo != undefined)
      $j('#addInfo').html(addInfo);
  if(gadgetInfo != undefined)
      $j('#gadgetInfo').html(gadgetInfo);

// connect the autoSubject to the input areas
  setUp("All");

// keep the demo and text columns the same size
  equalHeight(jQuery(".equal"));  
}  //end setup()


/*

   Carry common text to api example page

*/

function setUpExamplePage() {
   /*  Display text and other setup */
   
  // Use the ini file to set the main titles, etc.
  if(exampleMastheadTitle != undefined)
      $j('#masthead h1').html(exampleMastheadTitle);
  if(exampleMastheadSubTitle != undefined)
      $j('#masthead h2').html(exampleMastheadSubTitle);
  if(lastUpdate != undefined)
     $j('.foot-date').html(lastUpdate);  
  if(homeInfoAbout != undefined)
     $j('#homeInfo h3').html(homeInfoAbout);  
  if(projectTitle != undefined)
     $j('.projecttitle').html(projectTitle);  
  if(comments != undefined)
     $j('#feedback-form').html(comments);  

}  //end setUpExamplePage()

/*
  sets display view based on the radio box checked - clears everything on change 
 
*/

function changeDisplay(desiredView) {

    $j("#commonBoxField").css("display","none");
    $j("#breakerBoxField").css("display","none");
    $j("#connexBoxField").css("display","none");
    clearInput('commonbox');
    clearInput('breakerbox');
    clearInput('connexbox');
	 clearText('commonXtra','&nbsp;');
	 clearText('breakerXtra','&nbsp;');
	 clearText('connexXtra','6xx ?7 ');

    $j("#"+desiredView).css("display","block");
    
    return false;
  
}



/* 

 radio buttons don't see change functions - jquery fix 

*/
$j.fn.fix_radios = function() {
  function focus() {
    if ( !this.checked ) return;
    if ( !this.was_checked ) {
      $( this ).change();
    }
  }

  function change( e ) {
    if ( this.was_checked ) {
      e.stopImmediatePropagation();
      return;
    }
    $j( "input[name=" + this.name + "]" ).each( function() {
      this.was_checked = this.checked;
    } );
  }
  return this.focus( focus ).change( change );
} //end fn.fix_radios
/*
   attached the changeDisplay function to the radio buttons
 
*/

$j(function() {
  $j( "input[type=radio]" ).fix_radios();
  $j("input[name='displayType2']").change(function(){
    if ($j("input[@name='displayType2']:checked").val() == 'commonBoxField'){
       changeDisplay('commonBoxField');
    } else     if ($j("input[@name='displayType2']:checked").val() == 'breakerBoxField'){
       changeDisplay('breakerBoxField');
    } else changeDisplay('connexBoxField');

  });
});
