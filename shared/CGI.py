# Name:		CGI.py
# Purpose:	defines the CGI class (see below for details)

import time
import sys
import os
import cgi
import types

class CGI:
	# Concept:
	#	IS:   a CGI script, complete with logging and exception
	#	      handling
	#	HAS:  an error log and some parameters passed in
	#	DOES: parses parameters, logs messages, wraps main "program"
	#	      (method) in error handling
	# Implementation:

	def __init__ (self,
		logfilename = None	# string; name of log file to create
		):
		# Purpose: initializes the object and creates a log file with
		#	the specified name, if possible.  If no log file name
		#	is specified, we do not do logging.
		# Returns: nothing
		# Assumes: nothing
		# Effects: creates a log file in the OS
		# Throws: nothing
		# Notes: If we cannot create the log file, we write a message
		#	to sys.stderr.  So, look there if you are not finding
		#	the specified file.

		if logfilename is None:
			self.logfd = None
		else:
			try:
				self.logfd = open (logfilename, 'w')
			except:
				self.logfd = sys.stderr
				self.log ('Could not open log file %s' % \
					logfilename)
				self.logfd = None
		self.fields = {}
		self.contentType = 'text/html'
		return

	def log (self,
		message		# string; message to write to log file
		):
		# Purpose: writes a message to the log file (if one exists)
		# Returns: nothing
		# Assumes: nothing
		# Effects: writes to the log file
		# Throws: nothing
		# Notes: The format of the line written includes:
		#	script name: [date & time] [client IP] message\n

		if self.logfd is not None:
			cginame = os.path.basename (os.environ['SCRIPT_NAME'])
			datetime = time.asctime (time.localtime (time.time()))
			ip = os.environ['REMOTE_ADDR']
			self.logfd.write ('%s: [%s] [client %s] %s\n' % \
				(cginame, datetime, ip, message))
		return

	def get_parms (self,
		default_fields = None,	# dict; { fieldname : {
					#	    'op' : default operator,
					#	    'val' : default value } }
		default_types = None	# dict; { fieldname : type string }
		):
		# Purpose: get parameters passed into CGI script by GET or
		#	POST method
		# Returns: see Notes
		# Assumes: nothing
		# Effects: reads from stdin
		# Throws: propagates exceptions 
		# Notes: The default behavior of this method is to return a
		#	dictionary which has fieldnames as keys.  Each field-
		#	name is mapped to either a string (for single-valued
		#	fields) or a list of strings (for multi-valued
		#	fields).

		fs = cgi.FieldStorage()
		for key in fs.keys():
			if type(fs[key]) == types.ListType:
				self.fields[key] = []
				for item in fs[key]:
					self.fields[key].append (item.value)
			else:
				self.fields[key] = fs[key].value
		return self.fields

	def go (self):
		# Purpose: wraps the main() method in exception handling
		# Returns: nothing
		# Assumes: nothing
		# Effects: runs the main() method and outputs an explanatory
		#	HTML page if an error occurs
		# Throws: nothing

		print 'Content-type: %s' % self.contentType
		print

		try:
			self.main()
		except SystemExit:
			pass
		return

	def main (self):
		# Purpose: abstract method.  Conceptually, this is the "main
		#	program" of the CGI script.  Define this in a subclass
		#	for each CGI script.
		# Returns: nothing
		# Assumes: nothing
		# Effects: nothing
		# Throws: nothing

		return

	def setContentType (self,
		contentType		# string; 'text/html' by default
		):
		# Purpose: change the content type to be sent out with the
		#	"Content-type" header.  This method must be called
		#	before the go() method is called.
		# Returns: nothing
		# Assumes: nothing
		# Effects: updates the content-type to be sent to the client
		#	in the headers
		# Throws: nothing

		self.contentType = contentType
		return

