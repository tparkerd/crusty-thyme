"""Unnamed VCF-output splitter (Working title: `cut`)

This module splits the output of a VCF (.012, .012.pos, and .012.indv) into
individual files by chromosome.

This was created because the original VCF files were often too large for normal
computers to handle them.

Args:
  genotypes (str): *Required.* .012 VCF output file
  positions (str): *Required.* .012.pos VCF output file
  individuals (str): *Required.* .012.indv VCF output file
  output directory (str): Target path to place generated files

"""
import argparse
import datetime
import fileinput as fi
import logging
import os
import re
import shutil
import sys

import pandas as pd
from tqdm import tqdm


def stripLine(line):
	"""Converts a tab-delimited string to a list. Each element is trimmed of
  surrounding whitespace.

	Args:
		str
	"""
	xs = line.split('\t')
	xs = [ x.strip() for x in xs ]
	# Replace missing calls (-1) with NA
	for i, x in enumerate(xs):
		if x == '-1':
			xs[i] = 'NA'
	return xs

def process(args):
  """General processing function that does all the heavy lifting in terms of
  reading the input files and splitting them into individual files based on
  chromosome (or scaffold)
  """
  # Get all of the output directory info and set up the folderimport shutil
  try:
    if os.path.isdir(args.outdir):
      shutil.rmtree(args.outdir)
    os.mkdir(args.outdir)
  except:
    raise


  # Pull out and create of the position files
  if args.debug:
    print('/============= .pos =============')
  posfp = fi.input(args.positions)
  # Get the number of SNPs
  length_of_positions_file = 0
  with open(args.positions, 'r') as tmpposfp:
    for line in tmpposfp:
      length_of_positions_file += 1

  erdbeere = {} # placeholder variable name
  last_observered_chromosome = None
  max_lineno = 0
  for line in tqdm(posfp, desc = "extract postions (by chromosome)", total = length_of_positions_file):
    line = stripLine(line)
    logging.debug(line)
    chromosome, snp = line

    # Pull out the string identifier for the chromosome
    # This varies between the input files
    # For example, the setaria diversity panel includes "Chr" before each 
    # actual integer to identify the chromosome
    # This was included because scaffolds were included in the sequencing
    # As such, I decided to parse the string identifier with regex and to allow
    # for the qualifying prefix to be optional
    # Therefore, if just a number is provided, then it is assumed to be a
    # chromosome
    pattern = '(?P<label>[a-zA-Z]+)?_?(?P<id_num>\d+)'
    prog = re.compile(pattern)
    match = prog.fullmatch(chromosome)
    logging.debug(match.groups())
    prefix = 'chr' # assume there is no match, and therefore a chromosome
    if match.group('label') is not None:
      prefix = f"{match.group('label').lower()}"

    # All genomic sequences (chr, scaffolds, etc.) should have a numeric value
    # paired with it
    if match.group('id_num') is None:
      raise Exception(f'Position file has invalid format. Genomic sequence object (e.g., chr or scaffold) does not include numeric identifier.')
    id_num = int(match.group('id_num'))

    chromosome = f'{prefix}{id_num}'
    
    # Once a new chromosome is encountered, initialize it
    if last_observered_chromosome != chromosome:
      last_observered_chromosome = chromosome
      erdbeere[chromosome] = {}
      erdbeere[chromosome]['data'] = {}
      erdbeere[chromosome]['data']['genotype'] = []
      erdbeere[chromosome]['min'] = posfp.lineno()
    erdbeere[chromosome]['max'] = posfp.lineno()


    filename = f'{args.outdir}/{chromosome}_{args.name}.012.pos'
    message = f"{id_num}\t{snp}\n"
    if args.write:
      with open(filename, 'a+') as ofp:
        ofp.write(message)
  # Make sure to define the upper bound for the last chromosome
  erdbeere[last_observered_chromosome]['max'] = posfp.lineno()

  logging.debug(erdbeere)

  # Find the pedigree name for each genotype
  indvxs = []
  with open(args.individuals, 'r') as indvfp:
    for line in indvfp:
      indvxs.append(stripLine(line))
  indvdf = pd.DataFrame(indvxs)
  # Copy the individual/line files
  for i, c in enumerate(erdbeere.keys()):
    dest = f'{args.outdir}/{c}_{args.name}.012.indv'
    logging.debug(dest)
    try:
      if args.write:
        shutil.copyfile(args.individuals, dest)
      logging.debug(f'Copying {args.individuals} to {dest}')
    except:
      raise
  logging.debug(indvdf)
  
  length_of_genotype_file = 0
  with open(args.genotypes, 'r') as tmp_genofp:
    length_of_genotype_file += 1

  # For each chromosome...
  for i, c in enumerate(erdbeere.keys()):
    chr_lowerbound = erdbeere[c]['min']
    chr_upperbound = erdbeere[c]['max'] + 1
    alias = c
    filename = f'{args.outdir}/{c}_{args.name}.012'
    # For each line in the genotype (.012) file... and literally the line as in pedigree
    with open(args.genotypes, 'r') as genofp:
      for line in tqdm(genofp, desc = f"extract genotype (by line) for {alias}", total = length_of_genotype_file):
        xs = stripLine(line)
        xss = xs[chr_lowerbound:chr_upperbound]
        message = '\t'.join(xss)
        with open(filename, 'a+') as chromome_genofp:
          if args.write:
            chromome_genofp.write(f"{message}\n")
          logging.debug(f"{message}")

def parseOptions():
  """
  Function to parse user-provided options from terminal
  """

  default_output_directory = f"unnamed_output_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
  parser = argparse.ArgumentParser()
  parser.add_argument("--verbose", action="store_true", help="Increase output verbosity")
  parser.add_argument("-v", "--version", action="version", version='%(prog)s 1.0-alpha')
  parser.add_argument("-g", "--genotypes", required = True,
            help="(required) .012 input file")
  parser.add_argument("-p", "--positions", required = True,
            help="(required) .012.pos input file")
  parser.add_argument("-i", "--individuals", required = True,
            help="(required) .012.indv input file")
  parser.add_argument("-o", "--outdir", required = False,
                      default = default_output_directory,
                      help="path of output directory")
  parser.add_argument("-n", "--name", default = "unnamed",
                      help = "name of species used in naming output files")
  parser.add_argument("--debug", action = "store_true", help = "enables --verbose and disables writes to disk")
  args = parser.parse_args()
  args.write = True

  if args.debug is True:
    args.verbose = True
    args.write = False

  logging_level = logging.INFO

  if args.debug:
    logging_level = logging.DEBUG
  
  logging_format = '%(asctime)s - %(levelname)s - %(filename)s %(lineno)d - %(message)s'
  logging.basicConfig(format=logging_format, level=logging_level)
  
  return args

if __name__=="__main__":
  args = parseOptions()
  process(args)
