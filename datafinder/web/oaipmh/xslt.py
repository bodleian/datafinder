# -*- coding: utf-8 -*-

import os.path, commands

class XSLT(object):

	"""
		Using saxon to generate xml files from a xsl style sheet.
		
		see http://www.saxonica.com/documentation/index.html#!using-xsl/commandline
	"""

	def __init__( self, saxon_file, logger=None ) :
		

			
		self.saxon = saxon_file
		self.logger = logger
		
		self.transform = None

	
	def generate( self, xml_file, xsl_file, output_file=None, params={} ) :
			
		if not os.path.exists( self.saxon ) :
			self._error( "Generating XSLT: Saxon tool not found at \"" + self.saxon + "\"" )
			
			return False
			
		if not os.path.exists( xml_file ) :
			self._error( "XML file not found at \"" + xml_file + "\"" )
			
			return False
			
		if not os.path.exists( xsl_file ) :
			
			self._error( "XSL file not found at \"" + xsl_file + "\"" )
			
			return False
			
	
		command = self._default_command()
		
		command += '-s:"' + xml_file + '" '
		command += '-xsl:"' + xsl_file + '" '
		
		if output_file:
			command += '-o:"' + output_file + '" '
			
		if params:
			for param in params:
				command += param + "=" + params[param]
			
		#print command
		
		returns = commands.getstatusoutput( command )
		
		#print returns
		
		if returns[0] != 0:
			# There has been an error!
			self._error( "Error executing saxon, using xml=\"" + xml_file + '"and xsl="' + xsl_file + '". Output follows:\n------\n' + returns[1] + "\n------ " )

			return False
			
		return True
		
	
	def _default_command( self ):
		command = 'java -cp "' + self.saxon +  '" net.sf.saxon.Transform -t '
			
		command += "-warnings:silent " # Don't output warnings
		command += "-versionmsg:off " # Don't output version warnings
		command += "-quit:on " # Exit when finished.

		return command

	def _error( self, message ):
		if self.logger:
			self.logger.error( self._wrap_message(message) )
		print "Error:" + message
	def _warning( self, message ):
		if self.logger:
			self.logger.warning( self._wrap_message(message) )
	def _info( self, message ):
		if self.logger:
			self.logger.info( self._wrap_message(message) )
	def _debug( self, message ):
		if self.logger:
			self.logger.debug( self._wrap_message(message) )
			
	def _wrap_message( self, message ):
		return "class XSLT() :: " + message

#if __name__ == '__main__' :
	
	# Run a quick test
	
#	xslt = XSLT( "saxon9he.jar" )
	#xslt.generate( "simple.xml", "simple.xsl", "test.xml" )
	
	#xslt.generate( "complex.xml", "complex.xsl", params={"outputDir": "output/"} )
#	xslt.generate( "data_file.rdf", "ads2rdf-tweaked.xsl", output_file="dc_manifest_file.rdf",params={"outputDir": self.datadir} )
	
	
	
	
	
	
	
	
