#!/usr/local/bin/python
"""
Take a SNP ID (Consensus SNP or Sub SNP), look up the data in the database,
	and print it out in a simple format.
"""

import sys
from snp_tests import snplib

if __name__ == '__main__':
	snp = snplib.getSnpByID(sys.argv[1])
	if not snp:
		raise Exception('Uknown SNP ID: %s' % sys.argv[1])

	snplib.printVerbose(snp)