"""
Test that the correct SS ID is chosen for (Sanger) consensus SNPs with multiple sub SNPs.
"""

import unittest
from datatest import DataTestCase, runQuery

# constants
pairs = [
	('rs234882546', 'ss644758810'),		# first two chosen by highest build ID
	('rs228894858', 'ss644784010'),
	('rs250650953', 'ss443168526'),		# second two chosen by highest numerical part
	('rs258049303', 'ss450621290'),
	]

class SSIDTestCase(unittest.TestCase, DataTestCase):
	def testChoiceOfSS(self):
		"""
		For each pair, check that the consensus SNP has been associated only with the expected sub SNP.
		"""
		
		for (consensusSnpID, subSnpID) in pairs:
			cmd = '''select 1
				from snp_accession
				where _MGIType_key = 30
					and accID = '%s'
				limit 1''' % consensusSnpID
			self.assertQueryCount(1, cmd, 'Unknown consensus SNP ID : %s' % consensusSnpID, 'SNP data out of date?')

			cmd = '''select 1
				from snp_accession
				where _MGIType_key = 31
					and accID = '%s'
				limit 1''' % subSnpID
			self.assertQueryCount(1, cmd, 'Unknown sub SNP ID : %s' % subSnpID, 'SNP data out of date?')

			cmd = '''select 1
				from snp_subsnp ss, snp_accession a
				where a._MGIType_key = 30
					and a.accID = '%s'
					and a._Object_key = ss._ConsensusSnp_key''' % consensusSnpID
			self.assertQueryCount(1, cmd, 'SubSNP count != 1 for: %s' % consensusSnpID)
			
			cmd = '''select 1
				from snp_subsnp ss, snp_accession a, snp_accession ssa
				where a._MGIType_key = 30
					and a.accID = '%s'
					and a._Object_key = ss._ConsensusSnp_key
					and ss._SubSnp_key = ssa._Object_key
					and ssa._MGIType_key = 31
					and ssa.accID = '%s' ''' % (consensusSnpID, subSnpID)
			self.assertQueryCount(1, cmd, 'Could not find ID %s for: %s' % (subSnpID, consensusSnpID))

def suite():
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(SSIDTestCase))
	return suite

if __name__ == '__main__':
	unittest.main()
