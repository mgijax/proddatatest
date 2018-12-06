#!/usr/local/bin/python
"""
Take a SNP ID (Consensus SNP or Sub SNP), look up the data in the database,
	and print it out in a simple format.
"""

import os
import sys
sys.path.insert(0, '/usr/local/mgi/live/lib/python')
#sys.path.insert(0, os.path.join(os.getcwd(), 'snp_tests'))
sys.path.insert(0, os.getcwd())
import pg_db
from shared import CGI
from snp_tests import snplib
import Profiler
profiler = Profiler.Profiler()
profiler.stamp('Initializing')

pairs = [
	('bhmgidb06ld..bluebob'),
	]

pair = pairs[0]

class SnpViewer (CGI.CGI):
	def main(self):
		parms = self.get_parms()
		print '<HTML><HEAD><TITLE>Snp Viewer</TITLE></HEAD><BODY>'
		self.initializeDb(parms)
		self.showForm(parms)
		print '<HR>'
		self.showSnp(parms)
		print '<HR>'
		print '<PRE>'
		profiler.stamp('Done')
		profiler.write()
		print '</PRE>'
		print '</BODY></HTML>'
		return
	
	def initializeDb(self, parms):
		global pair
		if 'pair' in parms:
			pair = parms['pair']

		[server, database]= pair.strip().split('..')
		pg_db.set_sqlLogin('mgd_public', 'mgdpub', server, database)
		profiler.stamp('Logged into %s..%s' % (server, database))
		return
			
	def showForm(self, parms):
		print '<H3>Simple SNP Viewer</H3>'
		print '<FORM ACTION="showSnpByID.cgi" METHOD="GET">'
		print '<B>Server/Database:</B>'
		print '<SELECT TYPE="select" NAME="pair">'

		for onePair in pairs:
			if pair == onePair:
				print '<OPTION SELECTED>%s</OPTION>' % pair
			else:
				print '<OPTION>%s</OPTION>' % onePair

		print '</SELECT>' 

		if 'snpID' in parms:
			snpID = parms['snpID']
		else:
			snpID = ''
			
		print '<B>SNP ID (rs or ss):</B>'
		print '<INPUT NAME="snpID" TYPE="text" SIZE="20" VALUE="%s">' % snpID
		print '<INPUT TYPE="submit">'
		print '</FORM>'
		profiler.stamp('Wrote form')
		return
	
	def showSnp(self, parms):
		if 'snpID' in parms:
			snp = snplib.getSnpByID(parms['snpID'])
			if not snp:
				profiler.stamp('Failed to find %s in db' % parms['snpID'])
				print 'Unknown SNP ID: %s' % parms['snpID']
			else:
				profiler.stamp('Retrieved data')
				print '<PRE>'
				snplib.printVerbose(snp)
				print '</PRE>'
				profiler.stamp('Wrote data')
		else:
			print 'No SNP specified'
		return
	
if __name__ == '__main__':
	SnpViewer().go()
