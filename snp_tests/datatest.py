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
# For tests that failed, keep track of any hints for suggested fixes.
HINTS = set([])

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

		# Ensure that subclass has implemented the hints attribute
		#	for indicating what might need to be fixed if the test fails

		if not hasattr(self, 'hints'):
			errMsg = self.__class__ + " does not implement 'hints' attribute"
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
		
	def assertNotEmpty(self, collection, msg=None):
		"""
		ensure that the collection is not empty, or fail
		"""
		try:
			self.assertTrue(len(collection) > 0, msg)
		except AssertionError, ae:
			self._recordAssertionFailure()
			raise
		
	def _recordAssertionFailure(self):
		global HINTS
		if hasattr(self, 'hints'):
			HINTS.update(self.hints)

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
	if HINTS:

		msg = """The following hints may help identify what to fix:\n"""

		hints = list(HINTS)
		hints.sort()
		for hint in hints:
			msg += "\t" + hint + "\n"

		log(msg)
