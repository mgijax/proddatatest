"""
Test that translations from raw function classes to the MGI vocabulary are valid.
"""

import unittest
from datatest import DataTestCase, runQuery

# constants
pairs = [
	('stop-lost', 'rs214952642'),
	('stop-gained', 'rs584021049'),
	('missense', 'rs218600550'),
	('synonymous-codon', 'rs587592675'),
	('reference', 'rs214952642'),
	('reference', 'rs584021049'),
	('reference', 'rs218600550'),
	('reference', 'rs587592675'),
	('intron-variant', 'rs584021049'),
	('intron-variant', 'rs587462797'),
	('intron-variant', 'rs580281772'),
	('upstream-variant-2KB', 'rs3023487'),
	('upstream-variant-2KB', 'rs214952642'),
	('upstream-variant-2KB', 'rs49051912'),
	('downstream-variant-500B', 'rs217725902'),
	('utr-variant-5-prime', 'rs49051912'),
	('utr-variant-3-prime', 'rs13460870'),
	('nc-transcript-variant', 'rs587462797'),
	('nc-transcript-variant', 'rs580281772'),
	('splice-donor-variant', 'rs580281772'),
	('splice-acceptor-variant', 'rs586861309'), 
	]

class FunctionClassTranslationTestCase(unittest.TestCase, DataTestCase):
	hints = [ 'Fxn class translations missing - check translation table?']

	def testFunctionClassTranslations(self):
		"""
		For each pair, check that the SNP has been associated with the proper translated function class.
		"""
		
		for (rawFxnClass, snpID) in pairs:
			cmd = '''select 1
				from snp_accession
				where _MGIType_key = 30
					and accID = '%s'
				limit 1''' % snpID
			self.assertQueryCount(1, cmd, 'Unknown SNP ID : %s' % snpID)

			cmd = '''select 1
				from mgi_translation
				where _TranslationType_key = 1014
					and badName = '%s'
				limit 1''' % rawFxnClass
			self.assertQueryCount(1, cmd, 'Could not find translation record for: %s' % rawFxnClass)
			
			cmd = '''select 1
				from snp_accession a, snp_consensussnp_marker c, voc_term t, mgi_translation x
				where a._MGIType_key = 30
					and a.accID = '%s'
					and a._Object_key = c._ConsensusSnp_key
					and c._Fxn_key = t._Term_key
					and t._Term_key = x._Object_key
					and x._TranslationType_key = 1014
					and x.badName = '%s'
					limit 1''' % (snpID, rawFxnClass)
			self.assertQueryCount(1, cmd, 'Function class mismatch for %s : %s' % (snpID, rawFxnClass))

def suite():
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(FunctionClassTranslationTestCase))
	return suite

if __name__ == '__main__':
	unittest.main()
