"""
Test that each chromosome has at least one consensus SNP
"""

import unittest
from datatest import DataTestCase, runQuery
import snplib

# constants


class ChromosomeTestCase(unittest.TestCase, DataTestCase):
	hints = []

	def testChromosomesHaveData(self):
		"""
		For each chromosome, test that at least one consensus SNP exists.
		"""
		chromosomes = [ '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
			'13', '14', '15', '16', '17', '18', '19', 'X', 'Y', 'MT' ]
		
		for chrom in chromosomes:
			cmd = '''select s._ConsensusSnp_key
				from snp_consensussnp s, snp_coord_cache c
				where c.chromosome = '%s'
					and c._ConsensusSnp_key = s._ConsensusSnp_key
				limit 1''' % chrom
			self.assertQueryCount(1, cmd, 'Chromosome %s has no SNPs' % chrom)
			
	def testSpecificSnps(self):
		"""
		For a certain specified set of SNPs, ensure that they are on the expected chromosome.
		"""
		snps = [
			('rs254397212', 'Y'),
			('rs213274717', 'Y'),
			('rs47887021', 'Y'),
			('rs48587681', 'Y'),
			('rs45850354', 'Y'),
			('rs107920735', 'Y'),
			]
		
		for (snpID, chromosome) in snps:
			snp = snplib.getSnpByID(snpID)
			self.assertDataTrue(snp != None, 'Unknown SNP ID: %s' % snpID)
			
			# ensure the SNP has at least one location
			self.assertNotEmpty(snp.locations, 'SNP has no locations: %s' % snpID)
			
			found = False
			for location in snp.locations:
				if location.chromosome == chromosome:
					found = True
					
			self.assertDataTrue(found, 'SNP is not on chromosome %s: %s' % (chromosome, snpID))

def suite():
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(ChromosomeTestCase))
	return suite

if __name__ == '__main__':
	unittest.main()
