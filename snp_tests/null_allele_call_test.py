"""
Test that certain consensus SNPs have at least one null allele call
"""

import unittest
import snplib
from datatest import DataTestCase, runQuery

class NullAlleleCallTestCase(unittest.TestCase, DataTestCase):
	hints = [ 'Expected null allele calls were not found - has data changed?']

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
			self.assertDataTrue(snp != None, 'Unknown SNP ID: %s' % snpID)
			
			# ensure that there's at least one allele call for the SNP
			self.assertNotEmpty(snp.alleleCalls, 'SNP has no allele calls: %s' % snpID)
			
			# and ensure that there's at least one strain with no allele call for the SNP
			self.assertNotEmpty(sangerStrainSet.difference(snplib.strainsWithCalls(snp.alleleCalls)),
				'SNP has alleles for all strains: %s' % snpID)

def suite():
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(NullAlleleCallTestCase))
	return suite

if __name__ == '__main__':
	unittest.main()
