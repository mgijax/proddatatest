#!/usr/local/bin/python
"""
Test plan for ensuring that database is in a valid
	state for public release

Reports any data components that fail to meet tests.
Reports possible remedies (E.g. which cache loads might need to be rerun)
"""

import sys
import unittest

from shared import datatest
from snp_tests import *
from so_load_tests import *

def master_suite():
	"""
	Define which tests to run in order to test that
	database is ready for public release
	"""
	suites = []

	suites.append(location_test.suite())
	suites.append(function_class_translation_test.suite())
	suites.append(vocab_term_test.suite())
	suites.append(ss_id_test.suite())
	suites.append(consensus_alleles_test.suite())
	suites.append(so_vocab_test.suite())
	master_suite = unittest.TestSuite(suites)

	return master_suite


if __name__ == '__main__':

	# run test suites
	test_suite = master_suite()
	runner = unittest.TextTestRunner()
	ret = not runner.run(test_suite).wasSuccessful()
	
	# report any failures
	datatest.reportFailures()

	# return proper error code
	sys.exit(ret)
