# Name: snplib.py
# Purpose: general-purpose functions and classes to aid writing SNP tests

import types
import pg_db

###--- constants ---###

CONSENSUS_SNP_TYPE = 30
SUB_SNP_TYPE = 31
SNP_MARKER_TYPE = 32
SNP_POPULATION_TYPE = 33

REFSNP_LDB = 73
SUBSNP_LDB = 74
SUBMITTERSNP_LDB = 75
SUBSNP_POPULATION_LDB = 76

# names of strains expected to be in the Sanger SNP data set (plus C57BL/6J)
SANGER_STRAINS = [
	'129P2/OlaHsd',
	'129S1/SvImJ',
	'129S5/SvEvBrd',
	'AKR/J',
	'A/J',
	'BALB/cJ',
	'BTBR T<+> Itpr3<tf>/J',
	'BUB/BnJ',
	'C3H/HeH',
	'C3H/HeJ',
	'C57BL/10J',
	'C57BL/6NJ',
	'C57BR/cdJ',
	'C57L/J',
	'C58/J',
	'CAST/EiJ',
	'CBA/J',
	'DBA/1J',
	'DBA/2J',
	'FVB/NJ',
	'I/LnJ',
	'KK/HlJ',
	'LEWES/EiJ',
	'LP/J',
	'MOLF/EiJ',
	'NOD/ShiLtJ',
	'NZB/BlNJ',
	'NZO/HlLtJ',
	'NZW/LacJ',
	'PWK/PhJ',
	'RF/J',
	'SEA/GnJ',
	'SPRET/EiJ',
	'ST/bJ',
	'WSB/EiJ',
	'ZALENDE/EiJ',
	'C57BL/6J',
	]

###--- classes ---###

class ConsensusSnp:
	# Is: a single consensus SNP
	# Has: all attributes of a consensus SNP, including ID, locations,
	#	allele calls for strains, sub SNPs, etc.
	# Does: loads from the database all data for the SNP and exposes it
	#	via object traversal

	def __init__ (self, consensusSnpKey):
		self.consensusSnpKey = consensusSnpKey
		self.accID = None
		self.iupacCode = None
		self.variationType = None
		self.alleleSummary = None
		self.createdInBuild = None
		self.updatedInBuild = None
		self.flankBefore = None
		self.flankAfter = None

		self.orientation = None
		self.isMultiCoord = None
		self.alleleCalls = []
		self.subSnps = []
		self.locations = []

		self._initialize()
		return

	def _initialize (self):
		# basic SNP data
		cmd0 = '''select s.alleleSummary, s.iupacCode, s.buildCreated,
				s.buildUpdated, vc.term as variationType
			from SNP_ConsensusSnp s, VOC_Term vc
			where s._ConsensusSnp_key = %d
				and s._VarClass_key = vc._Term_key''' % self.consensusSnpKey
		results0 = pg_db.sql(cmd0, 'auto')
		if results0:
			self.alleleSummary = results0[0]['alleleSummary']
			self.iupacCode = results0[0]['iupacCode']
			self.createdInBuild = results0[0]['buildCreated']
			self.updatedInBuild = results0[0]['buildUpdated']
			self.variationType = results0[0]['variationType']
		
		# flanking sequences (5' is displayed first, then 3')
		cmd1 = '''select _ConsensusSnp_key, is5prime, sequenceNum, flank
			from snp_flank
			where _ConsensusSnp_key = %d
			order by is5prime, sequenceNum''' % self.consensusSnpKey
		results1 = pg_db.sql(cmd1, 'auto')
		
		seq1 = ''
		seq2 = ''
		for row in results1:
			if row['is5prime']:
				seq1 = seq1 + row['flank']
			else:
				seq2 = seq2 + row['flank']

		if seq1:
			self.flankBefore = seq1
		if seq2:
			self.flankAfter = seq2

		# primary ID for the SNP
		cmd2 = '''select accID
			from snp_accession
			where _MGIType_key = 30
			and _Object_key = %d''' % self.consensusSnpKey
		results2 = pg_db.sql(cmd2, 'auto')
		if results2:
			self.accID = results2[0]['accID']
		
		self._getAlleleCalls()
		self._getLocations()
		self._getSubSnps()
		return

	def _getAlleleCalls(self):
		cmd0 = '''select s.strain, a.allele, a.isConflict
			from snp_consensussnp_strainallele a, prb_strain s
			where _ConsensusSnp_key = %d
				and a._mgdStrain_key = s._Strain_key
				order by s.strain''' % self.consensusSnpKey
		results0 = pg_db.sql(cmd0, 'auto')
		
		for row in results0:
			self.alleleCalls.append(ConsensusSnpAlleleCall(row['strain'], row['allele'], row['isConflict']))
		return
	
	def _getSubSnps(self):
		cmd0 = '''select s._SubSnp_key
			from snp_subsnp s
			where s._ConsensusSnp_key = %d''' % self.consensusSnpKey
		results0 = pg_db.sql(cmd0, 'auto')
		
		for row in results0:
			self.subSnps.append(SubSnp(row['_SubSnp_key']))
		return
	
	def _getLocations(self):
		cmd0 = '''select s._Coord_Cache_key, s.sequenceNum
			from snp_coord_cache s
			where s._ConsensusSnp_key = %d
			order by s.sequenceNum''' % self.consensusSnpKey
		results0 = pg_db.sql(cmd0, 'auto')
		
		for row in results0:
			self.locations.append(ConsensusSnpLocation(row['_Coord_Cache_key']))
		return
	
class ConsensusSnpAlleleCall:
	def __init__ (self, strain, allele, isConflict):
		self.strain = strain
		self.allele = allele
		self.isConflict = isConflict
		return

class ConsensusSnpLocation:
	def __init__ (self, coordCacheKey):
		self.coordCacheKey = coordCacheKey
		self.chromosome = None
		self.startCoordinate = None
		self.isMultiCoord = None
		self.strand = None
		self.variationType = None
		self.alleleSummary = None
		self.iupacCode = None
		self.markers = []

		self._initialize()
		return

	def _initialize(self):
		cmd0 = '''select s.chromosome, s.startCoordinate, s.isMultiCoord, s.strand,
				vc.term as variationType, s.alleleSummary, s.iupacCode
			from snp_coord_cache s, voc_term vc
			where s._Coord_Cache_key = %d
				and s._VarClass_key = vc._Term_key''' % self.coordCacheKey
		results0 = pg_db.sql(cmd0, 'auto')
		if results0:
			self.chromosome = results0[0]['chromosome']
			self.alleleSummary = results0[0]['alleleSummary']
			self.iupacCode = results0[0]['iupacCode']
			self.variationType = results0[0]['variationType']
			self.strand = results0[0]['strand']
			self.isMultiCoord = results0[0]['isMultiCoord']
			self.startCoordinate = int(results0[0]['startCoordinate'])
			
		cmd1 = '''select _ConsensusSnp_Marker_key
			from snp_consensussnp_marker
			where _Coord_Cache_key = %d''' % self.coordCacheKey
		results1 = pg_db.sql(cmd1, 'auto')
		for row in results1:
			self.markers.append(ConsensusSnpMarker(row['_ConsensusSnp_Marker_key']))
		return

class ConsensusSnpMarker:
	def __init__ (self, consensusSnpMarkerKey):
		self.consensusSnpMarkerKey = consensusSnpMarkerKey
		self.markerKey = None
		self.markerSymbol = None
		self.markerID = None
		self.functionClass = None
		self.contigAllele = None
		self.residue = None
		self.aaPosition = None
		self.readingFrame = None
		self.distanceFrom = None
		self.distanceDirection = None
		self.proteinID = None
		self.transcriptID = None

		self._initialize()
		return

	def _initialize(self):
		cmd0 = '''select c._Marker_key, c.contig_allele, c.residue, c.aa_position, c.reading_frame,
				c.distance_from, c.distance_direction, m.symbol, a.accID, fc.term as functionClass,
				tp.transcriptID, tp.proteinID
			from snp_consensussnp_marker c
			inner join mrk_marker m on (c._Marker_key = m._Marker_key)
			inner join acc_accession a on (c._Marker_key = a._Object_key
				and a._MGIType_key = 2
				and a._LogicalDB_key = 1
				and a.preferred = 1
				and a.prefixPart = 'MGI:')
			inner join voc_term fc on (c._Fxn_key = fc._Term_key)
			left outer join snp_transcript_protein tp on (c._Transcript_Protein_key = tp._Transcript_Protein_key)
			where c._ConsensusSnp_Marker_key = %d''' % self.consensusSnpMarkerKey
		results0 = pg_db.sql(cmd0, 'auto')
		if results0:
			self.markerKey = results0[0]['_Marker_key']
			self.markerSymbol = results0[0]['symbol']
			self.markerID = results0[0]['accID']
			self.functionClass = results0[0]['functionClass']
			self.contigAllele = results0[0]['contig_allele']
			self.residue = results0[0]['residue']
			self.aaPosition = results0[0]['aa_position']
			self.readingFrame = results0[0]['reading_frame']
			self.distanceFrom = results0[0]['distance_from']
			self.distanceDirection = results0[0]['distance_direction']
			self.proteinID = results0[0]['proteinID']
			self.transcriptID = results0[0]['transcriptID']
		return

class SubSnp:
	# Is: a single sub[mitter] SNP
	# Has: all attributes of a subSNP, including submitter handle,
	#	allele calls for strains, variation class, etc.
	# Does: loads from the database all data for the subSNP and exposes it
	#	via object traversal

	def __init__ (self, subSnpKey):
		self.subSnpKey = subSnpKey
		self.variationType = None
		self.orientation = None
		self.isExemplar = None
		self.alleleSummary = None
		self.accID = None
		self.alleleCalls = []

		self._initialize()
		return

	def _initialize (self):
		cmd0 = '''select s.orientation, s.isExemplar, s.alleleSummary, vc.term as variationType, a.accID
			from snp_subsnp s
			inner join voc_term vc on (s._VarClass_key = vc._Term_key)
			left outer join snp_accession a on (a._MGIType_key = %d
				and a._Object_key = s._SubSnp_key
				and a._LogicalDB_key = %d)
			where s._SubSnp_key = %d''' % (SUB_SNP_TYPE, SUBSNP_LDB, self.subSnpKey)
		results0 = pg_db.sql(cmd0, 'auto')
		
		if results0:
			self.variationType = results0[0]['variationType']
			self.orientation = results0[0]['orientation']
			self.isExemplar = results0[0]['isExemplar']
			self.alleleSummary = results0[0]['alleleSummary']
			self.accID = results0[0]['accID']
			
		self._getAlleleCalls()
		return
	
	def _getAlleleCalls(self):
		cmd0 = '''select s.strain, a.allele, p.name as population
			from snp_subsnp_strainallele a, prb_strain s, snp_population p
			where a._SubSnp_key = %d
				and a._mgdStrain_key = s._Strain_key
				and a._Population_key = p._Population_key
			order by s.strain''' % self.subSnpKey
		results0 = pg_db.sql(cmd0, 'auto')
		
		for row in results0:
			self.alleleCalls.append(SubSnpAlleleCall(row['strain'], row['allele'], row['population']))
		return

class SubSnpAlleleCall:
	def __init__ (self, strain, allele, population):
		self.strain = strain
		self.allele = allele
		self.population = population
		return

###--- functions ---###

def getSnpByID(accID):
	# returns the ConsensusSnp or SubSnp object corresponding to the given accID, or None if no match

	cmd0 = '''select _MGIType_key, _Object_key
		from snp_accession
		where _MGIType_key in (30,31)
			and accID = '%s' ''' % accID
	results0 = pg_db.sql(cmd0, 'auto')
	
	if not results0:
		return None
	if results0[0]['_MGIType_key'] == CONSENSUS_SNP_TYPE:
		return ConsensusSnp(results0[0]['_Object_key'])
	return SubSnp(results0[0]['_Object_key'])

def printVerbose(obj, indentCount = 0, tail = ''):
	# print out a ConsensusSnp or SubSnp (or any other type of object) in a verbose format
	objType = type(obj)
	indent = '\t' * indentCount

	if objType == types.IntType:
		print '%s%d%s' % (indent, obj, tail)

	elif objType == types.StringType:
		print '%s%s%s' % (indent, obj, tail)

	elif objType == types.NoneType:
		print '%snull%s' % (indent, tail)

	elif objType == types.ListType:
		print '%s[' % indent
		for item in obj:
			printVerbose(item, indentCount + 1, ',')
		print '%s]' % indent

	elif objType == types.TupleType:
		print '%s(' % indent
		for item in obj:
			printVerbose(item, indentCount + 1, ',')
		print '%s)' % indent

	elif objType == types.InstanceType:
		print '%s{' % indent
		contents = dir(obj)
		for name in contents:
			if not name.startswith('_'):
				if type(eval('obj.%s' % name)) in [ types.StringType, types.IntType, types.NoneType ]:
					# print value on same line for simple fields
					print '%s%s:  ' % (indent, name),
					printVerbose(eval('obj.%s' % name), 0, ',')
				else:
					print '%s%s:' % (indent, name)
					printVerbose(eval('obj.%s' % name), indentCount + 1, ',')
		print '%s}%s' % (indent, tail)
	return

def strainsWithCalls(alleleCalls):
	# for the given list of allele calls, return a Set of the strains represented in it
	strains = set()
	for call in alleleCalls:
		strains.add(call.strain)
	return strains
