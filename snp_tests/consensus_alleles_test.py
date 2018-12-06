"""
Test that the expected number of distinct alleles were loaded for certain SNPs.
"""

import unittest
import snplib
from shared.datatest import DataTestCase, runQuery

def getAllele (alleleCalls, strain):
	# looks through the 'alleleCalls' to find and return the allele for the given 'strain',
	# or ' ' if there is no call for that strain

	if alleleCalls:
		for call in alleleCalls:
			if call.strain == strain:
				return call.allele
	return ' '
	
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

	def testAlleleCallsData(self):
		"""
		For each SNP in 'expectedCalls', verify that the allele calls match up with expectations.
		"""

		# expected allele calls for selected RefSNP IDs.  The string of allele calls is ordered
		# so each position corresponds to the strain of the same position in snplib.SANGER_STRAINS.
		# A space corresponds to no allele call for that strain.
		expectedCalls = {
			'rs584021049' : 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAATAAAA',
			'rs214952642' : 'TTTT  TT  TT   ATTTTT  TATTTT T  T TT',
			'rs580281772' : 'CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCTCCCC',
			'rs218600550' : 'TTTTTTTTTTTTTTTCTTTTTTTTTTTTTTTTTTTTT',
			'rs587592675' : 'AAAAAAAAAAAAAAAGAAAAAA AAAAAAAAA AAAA',
			'rs587462797' : 'TTTTTTTTTTTTTTTTTTTTTT TTTTTTTTTGTTTT',
			'rs3023487'   : 'AAAAAAAA AAAAAAA G A AAA AAAAAA GGAAA',
			'rs217725902' : 'GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGCGGGG',
			'rs49051912'  : 'TTTTCCTTCCTTTTTTCCCTCTTTTCTTTTTCTTTTT',
			'rs13460870'  : 'GGGGGGGGGGGGGGGGGGGGGGGGAGGGGAGGAGGGG',
			'rs586861309' : 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGAAAA',
			'rs581684779' : 'AAA A A AAAAAAAAAAA AAAA A  AG  GAAGA',
			'rs587233094' : 'TT TTT ATTAAAAATTTTTAT TATTATATTCATTA',
			'rs234882546' : 'GGGGGGGGGGGGGGGAGGGAGGGGAGGGGGGGGGGGG',
			'rs228894858' : 'AAAAAAATAATTTTTTAAAAAT ATATTTTAATTTTT',
			'rs52155783'  : ' C CCCCG CGGGGGGCCC  C C   CCCGC CC G',
			'rs582206682' : '                                    G',
			'rs47887021'  : '          A AAA  A  AA    A A  A    A',
			'rs48587681'  : '   G  GG  A AAA  A GAA  G A A GAGG GA',
		}

		# RS IDs from the above dictionary that should not be loaded (due to only a C57BL/6J call)
		noLoad = [ 'rs582206682' ]

		for snpID in expectedCalls:
			snp = snplib.getSnpByID(snpID)
			if snpID in noLoad:
				self.assertDataTrue(snp == None, 'Should not have loaded SNP ID: %s' % snpID, 'Test data out of date?')
				continue
			else:
				self.assertDataTrue(snp != None, 'Could not find SNP ID: %s' % snpID, 'SNP data out of date?')
				
				# check each allele for the SNP vs. its expected value
				index = 0
				for strain in snplib.SANGER_STRAINS:
					expectedAllele = expectedCalls[snpID][index]
					allele = getAllele(snp.alleleCalls, strain)
					self.assertDataTrue(expectedAllele == allele,
						'Mismatching allele for %s [%s - %s vs. %s]' % (snpID, strain, expectedAllele, allele),
						'SNP data out of date?')
					index = index + 1

def suite():
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(ConsensusAllelesTestCase))
	return suite

if __name__ == '__main__':
	unittest.main()
