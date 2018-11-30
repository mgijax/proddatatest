"""
datatest classes
"""
import logging
import os

if 'PYTHONPATH' in os.environ:
	import sys
	sys.path.insert(0, os.environ['PYTHONPATH'])

import pg_db

### Globals ###
# Track test failures
FAILURES = []
CACHELOADS = set([])
OTHERFIXES = set([])

### initialize database settings ###
pg_db.set_sqlUser('mgd_public')
pg_db.set_sqlPassword('mgdpub')
pg_db.set_sqlServer( os.environ['DATATEST_DBSERVER'] )
pg_db.set_sqlDatabase( os.environ['DATATEST_DBNAME'] )

### Classes ###

class DataTestCase(object):
	"""
	datatest Test Case
	Exposes special assertion methods

	Tracks and reports failures
	"""

	def __init__(self):

		# Ensure that subclass has implemented the cacheLoads attribute
		#	for tracking which cacheLoads the tested data is dependent on

		if (not hasattr(self, 'cacheLoads')) and (not hasattr(self, 'otherFixes')):
			errMsg = self.__class__ + " does not implement 'cacheLoads' or 'otherFixes' attribute"
			raise NotImplementedError(errMsg)


	def assertQueryCount(self, count, query, msg=None):
		"""
		Assert that the query returns count number of results
		"""
		results = runQuery(query)
		
		try:
			self.assertEquals(count, len(results), msg)
		except AssertionError, ae:
			self._recordAssertionFailure()
			raise

	def assertDataEquals(self, expected, actual, msg=None):
		"""
		Assert equals wrapper
		"""
		try:
			self.assertEquals(expected, actual, msg)
		except AssertionError, ae:
			self._recordAssertionFailure()
			raise

	def assertDataTrue(self, booleanValue, msg=None):
		"""
		AssertTrue wrapper
		"""
		try:
			self.assertTrue(booleanValue, msg)
		except AssertionError, ae:
			self._recordAssertionFailure()
			raise
		
	def _recordAssertionFailure(self):
		global CACHELOADS
		if hasattr(self, 'cacheLoads'):
			CACHELOADS.update(self.cacheLoads)
		if hasattr(self, 'otherFixes'):
			OTHERFIXES.update(self.otherFixes)


### methods ###

def runQuery(query):
	return pg_db.sql(query, 'auto')


def log(msg):
	print msg

def reportFailures():
	"""
	Report any test failures
	"""
	log('Tested %s..%s' % (os.environ['DATATEST_DBSERVER'], os.environ['DATATEST_DBNAME'] ))
	if CACHELOADS:

		msg = """The following cache loads may need to be rerun:\n"""

		cacheloads = list(CACHELOADS)
		cacheloads.sort()
		for cacheload in cacheloads:
			msg += "\t" + cacheload + "\n"

		log(msg)

	if OTHERFIXES:

		msg2 = """The following other fixes may be necessary:\n"""

		otherfixes = list(OTHERFIXES)
		otherfixes.sort()
		for otherfix in otherfixes:
			msg2 += "\t" + otherfix + "\n"

		log(msg2)
