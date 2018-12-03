"""
Test that each chromosome has at least one consensus SNP
"""

import unittest
from datatest import DataTestCase, runQuery

# constants


class NoEmptyChromosomesTestCase(unittest.TestCase, DataTestCase):
	hints = [ 'Some chromosomes have no SNPs -- are data files incomplete?']

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

def suite():
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(NoEmptyChromosomesTestCase))
	return suite

if __name__ == '__main__':
	unittest.main()
