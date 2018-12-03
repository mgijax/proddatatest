"""
Test foreign key relationships to ensure that terms are chosen from the expected vocabularies.
(Problems in these cannot be picked up just through referential integrity.)
"""

import unittest
from datatest import DataTestCase, runQuery

# (source table, FK in source table, name of expected vocabulary)
foreignKeys = [
	('snp_consensussnp', '_VarClass_key', 'SNP Variation Class'),
	('snp_coord_cache', '_VarClass_key', 'SNP Variation Class'),
	('snp_consensussnp_marker', '_Fxn_key', 'SNP Function Class'),
	('snp_population', '_SubHandle_key', 'SNP Submitter Handle'),
	('snp_subsnp', '_VarClass_key', 'SNP Variation Class'),
	('snp_subsnp', '_SubHandle_key', 'SNP Submitter Handle'),
	]

class VocabTermTestCase(unittest.TestCase, DataTestCase):
	hints = [ 'Some foreign keys refer to wrong vocabularies - error in load?']

	def testVocabTermChoices(self):
		"""
		For each tuple, check that the table.field only refers to terms for the desired vocabulary.
		"""
		
		for (table, field, vocab) in foreignKeys:
			cmd = '''select 1
				from voc_vocab
				where name = '%s'
				limit 1''' % vocab
			self.assertQueryCount(1, cmd, 'Cannot find vocab : %s' % vocab)

			cmd = '''with terms as (
					select distinct %s as _Term_key
					from %s
				)
				select 1
				from terms a, voc_term t, voc_vocab v
				where a._Term_key = t._Term_key
					and t._Vocab_key = v._Vocab_key
					and v.name != '%s'
				limit 1''' % (field, table, vocab)
			self.assertQueryCount(0, cmd, '%s.%s has terms other than from: %s' % (table, field, vocab))
			
def suite():
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(VocabTermTestCase))
	return suite

if __name__ == '__main__':
	unittest.main()
