"""
CSV Dataset Transformer

This is the original transformer that was meant to transform the long format of
traits by line, where the trait contains location and year. It splits a single
file into N files, where N is the number of location and year combinations.

Expected input: 2.from12.setaria.maf0.1.maxMissing0.1.allLines.012
  1 0       2       0       1       2       0       1       2       2       
  2 1       2       0       1       2       0       1       2       2       
  3 2       2       0       1       2       0       1       2       2       
  4 3       1       0       2       2       0       1       2       2       
  5 4       2       0       2       2       0       1       2       2       
  6 5       2       0       1       2       0       1       2       2       
  7 6       2       1       2       1       1       0       0       0       
  8 7       2       0       1       2       0       0       2       2       
  9 8       2       1       1       2       1       1       0       0       
  10 9       2       0       2       2       0       1       2       2      

In order to accomplish this, we can use `awk` to find the first instance of each
chromosome.

  $ awk -F'\t' '!a[$1]++{print NR":"$0}' inputfile.012
  1:Chr_01	110
  435559:Chr_02	8027
  954461:Chr_03	30108
  1540101:Chr_04	1773
  1927998:Chr_05	75259
  2426272:Chr_06	15444
  2848404:Chr_07	6930
  3223752:Chr_08	614
  3660804:Chr_09	14630
  4231903:scaffold_36	4187
  4232168:scaffold_43	20203

"""

import fileinput

import pandas as pd

from ..helpers import Convert, read_data
from pprint import pprint
from tqdm import tqdm
import itertools

def process(args, delimiter = ','):
  """Process data

  Args:
    args (Namespace): arguments supplied by user
    delimiter (String): value to split data, default ','
  """
  try:
    chrdata = {}
    fp = fileinput.input(args.files)
    current_chromosome = ''
    max_lineno = 0
    for line in fp:
      line = line.strip().split('\t')[0] # Pull out the chromosome name (e.g., Chr_01)
      # Change chromosome context if the current differs from the previous line
      if current_chromosome != line:
        current_chromosome = line
        chrdata[line] = {}
        # Record the line at which the change was made
        chrdata[line]['min'] = fp.lineno()

      # Update the max number for the current chromosome
      else:
        chrdata[line]['max'] = fp.lineno()

    pprint(chrdata)

    # Build a list (to be a Panda series) of all the chromosomes
    # The index in the list should be the line number, less 1. (lineno - 1)
    pseudo_chromosome_column = []
    line_column = []
    for index, chromosome in enumerate(chrdata):
        chromosome_min = chrdata[chromosome]['min']
        chromosome_max = chrdata[chromosome]['max']
        chromosome_diff = chromosome_max - chromosome_min
        pseudo_chromosome_column += [ chromosome for tmp in range(chromosome_diff + 1)] # Range excludes upperbound
        line_column += [ index for index in range(chromosome_diff + 1)] # Range excludes upperbound


    # pcc = pd.Series(pseudo_chromosome_column)
    # lc = pd.Series(line_column)
    # pprint(pcc)
    # pprint(lc)
    # df = pd.read_table(args.vcf_input, sep = '\t')
    # df.assign(pd.Series(pseudo_chromosome_column))
    # pprint(head(df[]))
    # pprint(df[[0,10]].iloc[0:10])

    # Read line-by-line 012 files and interleave them
    # NOTE(timp): This could be accomplished in bash with the following command:
    #             paste input.pos input.012

    total_line_count = 0
    with open(args.files[0]) as posfp:
        for i, l in enumerate(posfp):
            pass
    total_line_count = i + 1

    vcffp = open(args.vcf_input, 'r') # genotype datafile
    posfp = open(args.files[0], 'r') # chromosome position file
    tmpdf = open('.tmpdf', 'w')      # temporary data file to be loaded as pandas df
    for lines in tqdm(itertools.zip_longest(posfp, vcffp), desc="Genotype File", total=total_line_count):
      lines = [ line.strip() for line in lines ]
      tmpdf.write('\t'.join(lines))
    vcffp.close()
    posfp.close()
    tmpdf.close()


    # We have the line numbers once we switch chromosome context
    # So long as the queue is not empty and there are lines left, process the
    # VCF file.
    # Load the plain file




    # For each line...
    # vcf_fp = fileinput.input(args.vcf_input)
    # for line in vcf_fp:
    #   # For each known chromosome...
    #   for chromosome in chrdata:
    #     cur_lineno = vcf_fp.lineno()
    #     if cur_lineno >= chrdata[chromosome]['min'] and cur_lineno <= chrdata[chromosome]['max']:
    #       print(f"{chromosome}   {cur_lineno}")





















    # df = read_data(args, delimiter)

    # # Create a set of filenames and identifiers
    # # The filenames are used to access the data stored as dataframes,
    # # and the identifiers are used to filter the appropriate columns
    # # to omit irrelevant data in the output dataframe
    # filenames = set()
    # identifiers = set()
    # for trait in df.columns[1:]:
    #   filename = Convert.loyr_to_filename(trait)
    #   filenames.add(filename)
    #   identity = Convert.trait_to_identifier(trait)
    #   identifiers.add(identity)
    # filenames = sorted(list(filenames))
    # identifiers = sorted(list(identifiers))

    # dfs = {}
    # for index, filename in enumerate(filenames):
    #   dfs[filename] = {}
    #   dfs[filename]['filename'] = '.'.join([filename, 'csv'])
    #   identity = identifiers[index]
    #   # Create a regex pattern that joins the identifier with Boolean ORs
    #   # Also, make it so that it can be anywhere in the column name and be
    #   # included.
    #   pattern = f".*{'|'.join([list(df)[0], identity])}.*"
    #   # Only include relevant column, set row label as index, and drop any rows that have all missing values
    #   dfs[filename]['data'] = df.filter(regex = pattern).set_index(df.columns[0]).dropna(how = 'all')
    #   # Rename columns to omit location-year pairs
    #   dfs[filename]['data'].columns = [ Convert.trait_to_column(t) for t in dfs[filename]['data'].columns ]

    # # Return the resultant dataframes
    # return dfs

  except:
    raise 

  # In case something went wrong, return None and test for that on response
  return None

