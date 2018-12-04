"""
Test that the expected number of distinct alleles were loaded for certain SNPs.
"""

import unittest
import snplib
from datatest import DataTestCase, runQuery

class ConsensusAllelesTestCase(unittest.TestCase, DataTestCase):
	def testAlleleCounts(self):
		"""
		For each pair, check that the consensus SNP has the expected number of distinct alleles.
		"""
		pairs = [
			('rs582507352', 3),
			('rs587233094', 3),
			]

		for (snpID, alleleCount) in pairs:
			cmd = '''select 1
				from snp_accession
				where _MGIType_key = 30
					and accID = '%s'
				limit 1''' % snpID
			self.assertQueryCount(1, cmd, 'Unknown SNP ID : %s' % snpID, 'SNP data out of date?')

			cmd = '''select distinct s.allele
				from snp_accession a, snp_consensussnp_strainallele s
				where a._MGIType_key = 30
					and a.accID = '%s'
					and a._Object_key = s._ConsensusSnp_key''' % snpID
			self.assertQueryCount(alleleCount, cmd, 'Wrong number of alleles for SNP ID : %s' % snpID)

	def testRefSnpsHaveNullCalls(self):
		"""
		For each RefSNP, check that at least one allele call is null (missing).
		"""
		# new SNPs to come in with Sanger data:
		snps = [ 'rs214952642', 'rs581684779', 'rs587233094' ]

		sangerStrainSet = set()
		for strain in snplib.SANGER_STRAINS:
			sangerStrainSet.add(strain)
		
		for snpID in snps:
			snp = snplib.getSnpByID(snpID)
			self.assertDataTrue(snp != None, 'Unknown SNP ID: %s' % snpID, 'SNP data out of date?')
			
			# ensure that there's at least one allele call for the SNP
			self.assertNotEmpty(snp.alleleCalls, 'SNP has no allele calls: %s' % snpID)
			
			# and ensure that there's at least one strain with no allele call for the SNP
			self.assertNotEmpty(sangerStrainSet.difference(snplib.strainsWithCalls(snp.alleleCalls)),
				'SNP has alleles for all strains: %s' % snpID)

	def testRefSnpsHaveAllCalls(self):
		"""
		For each RefSNP, check that all Sanger + B6 strains have an allele call.
		"""
		# new SNPs to come in with Sanger data:
		snps = [ 'rs587462797', 'rs584021049', 'rs214952642' ]

		sangerStrainSet = set()
		for strain in snplib.SANGER_STRAINS:
			sangerStrainSet.add(strain)
		
		for snpID in snps:
			snp = snplib.getSnpByID(snpID)
			self.assertDataTrue(snp != None, 'Unknown SNP ID: %s' % snpID, 'SNP data out of date?')
			
			# ensure that there's at least one allele call for the SNP
			self.assertNotEmpty(snp.alleleCalls, 'SNP has no allele calls: %s' % snpID)
			
			# and ensure that there's at least one strain with no allele call for the SNP
			missingCalls = sangerStrainSet.difference(snplib.strainsWithCalls(snp.alleleCalls))
			self.assertDataTrue(len(missingCalls) == 0,
				'SNP is missing calls for %d alleles: %s' % (len(missingCalls), snpID))

def suite():
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(ConsensusAllelesTestCase))
	return suite

if __name__ == '__main__':
	unittest.main()
