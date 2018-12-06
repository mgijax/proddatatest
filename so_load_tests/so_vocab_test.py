"""
Basic set of tests for the Sequence Ontology (SO), currently loaded as a flat vocabulary
"""

import unittest
from shared.datatest import DataTestCase, runQuery

class SOVocabTestCase(unittest.TestCase, DataTestCase):
	def testVocabExists(self):
		"""
		Test that the vocabulary itself exists.
		"""
		cmd = '''select 1
			from voc_vocab
			where name = 'Sequence Ontology' '''
		self.assertQueryCount(1, cmd, 'Sequence Ontology does not exist in VOC_Vocab', 'Need to add to VOC_Vocab')

	def testVocabIsSimple(self):
		"""
		Test that the vocabulary is a sipmle vocabulary.
		"""
		cmd = '''select 1
			from voc_vocab
			where name = 'Sequence Ontology'
			and isSimple = 1'''
		self.assertQueryCount(1, cmd, 'Sequence Ontology exists in VOC_Vocab, but isSimple = 0', 'SO should be a flat vocab')
		
	def testNoDAG(self):
		"""
		Test that the SO vocabulary has no associated DAG
		"""
		cmd = '''select 1
			from voc_vocab v, voc_vocabdag d
			where v.name = 'Sequence Ontology'
				and v._Vocab_key = d._Vocab_key
			limit 1'''
		self.assertQueryCount(0, cmd, 'Sequence Ontology has an associated DAG', 'SO should have no DAG in VOC_VocabDAG')
		
	def testTermsExist(self):
		"""
		Test that at least one SO term exists.
		"""
		cmd = '''select 1
			from voc_vocab v, voc_term t
			where v.name = 'Sequence Ontology'
				and v._Vocab_key = t._Vocab_key
			limit 1'''
		self.assertQueryCount(1, cmd, 'Sequence Ontology has no terms in VOC_Term', 'Is there an issue with the so.obo data file?')

	def testSynonymsExist(self):
		"""
		Test that at least one synonym exists for a SO term.
		"""
		cmd = '''select 1
			from mgi_synonymtype st, mgi_synonym s, voc_term t, voc_vocab v
			where st._MGIType_key = 13
				and st._SynonymType_key = s._SynonymType_key
				and s._Object_key = t._Term_key
				and t._Vocab_key = v._Vocab_key
				and v.name = 'Sequence Ontology'
			limit 1'''
		self.assertQueryCount(1, cmd, 'Sequence Ontology has no synonyms in MGI_Synonym', 'Is there an issue with the so.obo data file?')

	def testNotesExist(self):
		"""
		Test that at least one note (definition) exists for a SO term.
		"""
		cmd = '''select 1
			from mgi_notetype nt, mgi_note n, mgi_notechunk c, voc_term t, voc_vocab v
			where nt._MGIType_key = 13
				and nt._NoteType_key = n._NoteType_key
				and n._Note_key = c._Note_key
				and n._Object_key = t._Term_key
				and t._Vocab_key = v._Vocab_key
				and v.name = 'Sequence Ontology'
			limit 1'''
		self.assertQueryCount(1, cmd, 'Sequence Ontology has no notes in MGI_Note', 'Is there an issue with the so.obo data file?')

	def testIDsExist(self):
		"""
		Test that at least one accession ID exists for a SO term.
		"""
		cmd = '''select 1
			from acc_accession a, voc_term t, voc_vocab v
			where a._MGIType_key = 13
				and a._Object_key = t._Term_key
				and t._Vocab_key = v._Vocab_key
				and v.name = 'Sequence Ontology'
			limit 1'''
		self.assertQueryCount(1, cmd, 'Sequence Ontology has no IDs in ACC_Accession', 'Is there an issue with the so.obo data file?')
			
def suite():
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(SOVocabTestCase))
	return suite

if __name__ == '__main__':
	unittest.main()
