"""
Test that the expected number of distinct alleles were loaded for certain SNPs.
"""

import unittest
from datatest import DataTestCase, runQuery

# constants
pairs = [
	('rs582507352', 3),
	('rs587233094', 3),
	]

class ConsensusAllelesTestCase(unittest.TestCase, DataTestCase):
	hints = []

	def testAlleleCounts(self):
		"""
		For each pair, check that the consensus SNP has the expected number of distinct alleles.
		"""
		
		for (snpID, alleleCount) in pairs:
			cmd = '''select 1
				from snp_accession
				where _MGIType_key = 30
					and accID = '%s'
				limit 1''' % snpID
			self.assertQueryCount(1, cmd, 'Unknown SNP ID : %s' % snpID)

			cmd = '''select distinct s.allele
				from snp_accession a, snp_consensussnp_strainallele s
				where a._MGIType_key = 30
					and a.accID = '%s'
					and a._Object_key = s._ConsensusSnp_key''' % snpID
			self.assertQueryCount(alleleCount, cmd, 'Wrong number of alleles for SNP ID : %s' % snpID)

def suite():
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(ConsensusAllelesTestCase))
	return suite

if __name__ == '__main__':
	unittest.main()
