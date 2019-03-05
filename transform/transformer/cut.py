"""PandaPiper"""
import pandas as pd
import os
import sys
import fileinput as fi
import datetime
import argparse
import shutil
from pprint import pprint
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

  if args.debug:
    print('/============= .pos =============')
  posfp = fi.input(args.positions)
  length_of_positions_file = 0
  with open(args.positions, 'r') as tmpposfp:
    for line in tmpposfp:
      length_of_positions_file += 1
  erdbeere = {}
  current_chromosome = None
  max_lineno = 0
  for line in tqdm(posfp, desc = "extract postions (by chromosome)", total = length_of_positions_file):
    line = stripLine(line)
    if args.debug:
      print(line)
    chromosome, snp = line
    if current_chromosome != chromosome:
      current_chromosome = chromosome
      erdbeere[chromosome] = {}
      erdbeere[chromosome]['data'] = {}
      erdbeere[chromosome]['data']['genotype'] = []
      erdbeere[chromosome]['min'] = posfp.lineno()
    erdbeere[chromosome]['max'] = posfp.lineno()
    prefix = current_chromosome[:3].lower()
    id_num = str(int(current_chromosome[-2:]))
    filename = f'{args.outdir}/{prefix}{id_num}_{args.name}.012.pos'
    message = f"{str(int(current_chromosome[-2:]))}\t{snp}\n"
    with open(filename, 'a+') as ofp:
      ofp.write(message)
  # Make sure to define the upper bound for the last chromosome
  erdbeere[current_chromosome]['max'] = posfp.lineno()

  if args.verbose:
    pprint(erdbeere)

  # Find the pedigree name for each genotype
  indvxs = []
  with open(args.individuals, 'r') as indvfp:
    for line in indvfp:
      indvxs.append(stripLine(line))
  indvdf = pd.DataFrame(indvxs)
  # Copy the individual/line files
  for i, c in enumerate(erdbeere.keys()):
    dest = f'{args.outdir}/{c[:3].lower()}{str(int(c[-2:]))}_{args.name}.012.indv'
    try:
      if not args.debug:
        shutil.copyfile(args.individuals, dest)
      if args.verbose:
        print(f'Copying {arg.individuals} to {dest}')
    except:
      raise
  if args.verbose:
    pprint(indvdf)
  
  # # Cut out the columns for each
  # genoxs = []
  # # Count the number of lines in the genotype table for progress info
  # length_of_genotype_file = 0
  # with open(args.genotypes, 'r') as tmp_genofp:
  #   length_of_genotype_file += 1
  # with open(args.genotypes, 'r') as genofp:
  #   for line in tqdm(genofp, desc="extract genotype (by line)", total = length_of_genotype_file):
  #     xs = stripLine(line)
  #     # For each chromosome, pull out the columns from the genotype
  #     for i, c in enumerate(erdbeere.keys()):
  #       chr_lowerbound = erdbeere[c]['min']
  #       chr_upperbound = erdbeere[c]['max'] + 1
  #       xss = xs[chr_lowerbound:chr_upperbound]
  #       c = f'{c[:3].lower()}{str(int(c[-2:]))}_{args.name}.012'
  #       filename = f'{args.outdir}/{c}'
  #       message = '\t'.join(xss)
  #       with open(filename, 'a+') as chromome_genofp:
  #         if not args.debug:
  #           chromome_genofp.write(f"{message}\n")
  #         if args.verbose:
  #           print(f"{message}")

  length_of_genotype_file = 0
  with open(args.genotypes, 'r') as tmp_genofp:
    length_of_genotype_file += 1

  # For each chromosome...
  for i, c in enumerate(erdbeere.keys()):
    chr_lowerbound = erdbeere[c]['min']
    chr_upperbound = erdbeere[c]['max'] + 1
    alias = c
    c = f'{c[:3].lower()}{str(int(c[-2:]))}_{args.name}.012'
    filename = f'{args.outdir}/{c}'
    # For each line in the genotype (.012) file... and literally the line as in pedigree
    with open(args.genotypes, 'r') as genofp:
      for line in tqdm(genofp, desc = f"extract genotype (by line) for {alias}", total = length_of_genotype_file):
        xs = stripLine(line)
        xss = xs[chr_lowerbound:chr_upperbound]
        message = '\t'.join(xss)
        with open(filename, 'a+') as chromome_genofp:
          if not args.debug:
            chromome_genofp.write(f"{message}\n")
          if args.verbose:
            print(f"{message}")


def parseOptions():
  """
  Function to parse user-provided options from terminal
  """

  default_output_directory = f"unnamed_output_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
  parser = argparse.ArgumentParser()
  parser.add_argument("-v", "--verbose", action="store_true",
                      help="increase output verbosity")
  parser.add_argument("-g", "--genotypes", required = True,
            help="(required) .012 input file")
  parser.add_argument("-p", "--positions", required = True,
            help="(required) .012.pos input file")
  parser.add_argument("-i", "--individuals", required = True,
            help="(required) .012.indv input file")
  parser.add_argument("-o", "--outdir", required = True,
                      default = default_output_directory,
                      help="path of output directory")
  parser.add_argument("-n", "--name", default = "unnamed",
                      help = "name of species used in naming output files")
  parser.add_argument("--debug", action = "store_true", help = "enables --verbose and disables writes to disk")
  args = parser.parse_args()
  if args.debug is True:
    args.verbose = True
  
  return args

if __name__=="__main__":
  args = parseOptions()
  process(args)
