"""
Test that certain consensus SNPs have an allele call for all strains in the Sanger + B6 set
"""

import unittest
import snplib
from datatest import DataTestCase, runQuery

class AllAlleleCallTestCase(unittest.TestCase, DataTestCase):
	hints = [ 'Found null allele calls where none were expected - were all data loaded?']

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
			self.assertDataTrue(snp != None, 'Unknown SNP ID: %s' % snpID)
			
			# ensure that there's at least one allele call for the SNP
			self.assertNotEmpty(snp.alleleCalls, 'SNP has no allele calls: %s' % snpID)
			
			# and ensure that there's at least one strain with no allele call for the SNP
			missingCalls = sangerStrainSet.difference(snplib.strainsWithCalls(snp.alleleCalls))
			self.assertDataTrue(len(missingCalls) == 0,
				'SNP is missing calls for %d alleles: %s' % (len(missingCalls), snpID))

def suite():
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(AllAlleleCallTestCase))
	return suite

if __name__ == '__main__':
	unittest.main()
