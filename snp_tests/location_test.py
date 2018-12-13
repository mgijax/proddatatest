"""
Tests involving SNP locations (chromosome + coordinate)
"""

import unittest
from shared.datatest import DataTestCase, runQuery
import snplib

class LocationTestCase(unittest.TestCase, DataTestCase):
	def testChromosomesHaveSnps(self):
		"""
		For each chromosome, test that at least one consensus SNP exists.
		"""
		chromosomes = [ '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
			'13', '14', '15', '16', '17', '18', '19', 'X', 'Y', 'MT' ]
		
		# doing the query this way rather than iterating over chromosomes is only 1 table scan
		cmd = '''select distinct chromosome
				from snp_coord_cache
				where chromosome in ('%s')''' % "', '".join(chromosomes)
		
		self.assertQueryCount(len(chromosomes), cmd, 'Some chromosomes do not have SNPs', 'Missing data files?')
			
	def testJustChromosomes(self):
		"""
		For a certain specified set of SNPs, ensure that they are on the expected chromosome.
		"""
		snps = [
			('rs584021049', '19'),
			('rs214952642', '19'),
			('rs580281772', '19'),
			('rs218600550', '19'),
			('rs587592675', '19'),
			('rs587462797', '19'),
			('rs3023487', '19'),
			('rs217725902', '19'),
			('rs49051912', '19'),
			('rs13460870', '19'),
			('rs586861309', '19'),
			('rs581684779', '19'),
			('rs587233094', '19'),
			('rs234882546', '19'),
			('rs228894858', '19'),
			('rs52155783', '19'),
			('rs586195285', '18'),
			('rs247969879', '18'),
			('rs45734785', '19'),
			]
		
		for (snpID, chromosome) in snps:
			snp = snplib.getSnpByID(snpID)
			self.assertDataTrue(snp != None, 'Unknown SNP ID: %s' % snpID, 'SNP data out of date?')
			
			# ensure the SNP has at least one location
			self.assertNotEmpty(snp.locations, 'SNP has no locations: %s' % snpID)
			
			found = False
			for location in snp.locations:
				if location.chromosome == chromosome:
					found = True
					
			self.assertDataTrue(found, 'SNP is not on chromosome %s: %s' % (chromosome, snpID))
	
	def testCoordinates(self):
		"""
		For a certain specified set of SNPs, check chromosome + coordinate assignments.
		"""
		snps = [
			('rs586195285', '18', 3000024),
			('rs247969879', '18', 3000323),
			('rs45734785', '19', 53244501),
			]

		for (snpID, chrom, coord) in snps:
			snp = snplib.getSnpByID(snpID)
			self.assertDataTrue(snp != None, 'Unknown SNP ID: %s' % snpID, 'SNP data out of date?')
			
			# ensure the SNP has at least one location
			self.assertNotEmpty(snp.locations, 'SNP has no locations: %s' % snpID)
			
			found = False
			for location in snp.locations:
				if location.chromosome == chrom:
					if int(location.startCoordinate) == coord:
						found = True
					
			self.assertDataTrue(found, 'SNP %s is not at Chr%s:%d' % (snpID, chrom, coord))

def suite():
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(LocationTestCase))
	return suite

if __name__ == '__main__':
	unittest.main()
