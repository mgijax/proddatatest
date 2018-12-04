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

	hints = []

	def assertQueryCount(self, count, query, msg=None, hint=None):
		"""
		Assert that the query returns count number of results
		"""
		results = runQuery(query)
		
		try:
			self.assertEquals(count, len(results), msg)
		except AssertionError, ae:
			self._recordAssertionFailure()
			self._addHint(hint)
			raise

	def assertDataEquals(self, expected, actual, msg=None, hint=None):
		"""
		Assert equals wrapper
		"""
		try:
			self.assertEquals(expected, actual, msg)
		except AssertionError, ae:
			self._recordAssertionFailure()
			self._addHint(hint)
			raise

	def assertDataTrue(self, booleanValue, msg=None, hint=None):
		"""
		AssertTrue wrapper
		"""
		try:
			self.assertTrue(booleanValue, msg)
		except AssertionError, ae:
			self._recordAssertionFailure()
			self._addHint(hint)
			raise
		
	def assertNotEmpty(self, collection, msg=None, hint=None):
		"""
		ensure that the collection is not empty, or fail
		"""
		try:
			self.assertTrue(len(collection) > 0, msg)
		except AssertionError, ae:
			self._recordAssertionFailure()
			self._addHint(hint)
			raise
		
	def _recordAssertionFailure(self):
		global HINTS
		HINTS.update(self.hints)

	def _addHint(self, hint):
		if hint and (hint not in self.hints):
			self.hints.append(hint)

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
