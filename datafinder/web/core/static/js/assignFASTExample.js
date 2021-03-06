jQuery.noConflict();  


/*
    javascript in this file controls the html page demonstrating the autosubject functionality

*/



/**************************************************************************************/
/*              Set up and initialization */
/**************************************************************************************/
/*
initial setup - called from onLoad
  attaches the autocomplete function to the search box
*/


var currentSuggestIndexDefault = "suggest50";  //initial default value

function setUpPage() {
// connect the autoSubject to the input areas

    //jQuery('div :input.subject_area').autocomplete({
    // the following autocomplete  function works for dynamically added input fields 
    jQuery('div :input.subject_area').live("focus.autocomplete", null, function () {
            jQuery(this).autocomplete({ 
          source: autoSubjectExample, 
          minLength: 1,
   		 select: function(event, ui) {
              jQuery('#exampleXtra').html("FAST ID <b>" + ui.item.idroot + "</b> Facet <b>"+ getTypeFromTag(ui.item.tag)+ "</b>");
          } //end select
      } 
   ).data( "autocomplete" )._renderItem = function( ul, item ) { formatSuggest(ul, item);};
});
}  //end setUpPage()

/*  
    example style - simple reformatting
*/
function autoSubjectExample(request, response) {
  currentSuggestIndex = currentSuggestIndexDefault;
  autoSubject(request, response, exampleStyle);
}

/*
  For this example, replace the common subfield break of -- with  /
  */
  
function exampleStyle(res) {
  return res["auth"].replace("--","/"); 
   
}
