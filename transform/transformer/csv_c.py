"""
CSV Dataset Transformer C

Transforms Setaria Diversity Panel (uncertain)'s MLMM GWAS results into 
consumable phenotype files. Unfortunately, the growout information is 
currently not known for this type of file. The only information to
differentiate each is the date within the month and its treatment.

Expected input file: 2.Setaria_IR_2016_datsetset_GWAS.BLUPsandBLUEs.csv
  Genotype 	Jul_11_IR_dry     	Jul_11_IR_wet	  Jul_16_IR_dry	  Jul_16_IR_wet ...
  A10     	36.92125          	33.92521875	    NA	            27.4225
  B100      36.4654705882353    33.40457	      31.123065	      29.6538846153846
  TB_0003   35.889          	  32.43496875	    31.1626875	    27.5370625
  TB_0006   35.72659375         32.79684375	    28.989875	      27.98225
  TB_0010   36.48159375        34.2420625	      31.6885625	    30.9990625
  ...

Note:
  The contents of this file were simply the averages of the raw phenotypic data
  provided in `Setaria_IR_2016_datsetset_GWAS.csv`.

Expected input format:
  N files, M traits, P lines
  Line/Pedigree, Trait 1, Trait 2, Trait 3, ...Trait M
  Line 1, 1, 2, 3, 4, 5...M
  Line 2, 1, 2, 3, 4, 5...M
  ...
  Line P, 1, 2, 3, 4, 5...M

Example output files:

"""
import fileinput

import pandas as pd

from transform.util.convert import (loyr_to_filename, trait_to_column,
                                    trait_to_identifier)
from transform.util.helpers import read_data


def process(args, delimiter = ','):
  """Process data

  Args:
    args (Namespace): arguments supplied by user
    delimiter (str): value to split data, default ','
  
  """
  try:
    df = read_data(args, delimiter)

    # Create a set of filenames and identifiers
    # The filenames are used to access the data stored as dataframes,
    # and the identifiers are used to filter the appropriate columns
    # to omit irrelevant data in the output dataframe
    filenames = set()
    identifiers = set()
    for trait in df.columns[1:]:
      filename = loyr_to_filename(trait)                  # UPDATE THIS CODE BLOCK
      filenames.add(filename)                             # UPDATE THIS CODE BLOCK
      identity = trait_to_identifier(trait)               # UPDATE THIS CODE BLOCK
      identifiers.add(identity)                           # UPDATE THIS CODE BLOCK
    filenames = sorted(list(filenames))                   # UPDATE THIS CODE BLOCK
    identifiers = sorted(list(identifiers))               # UPDATE THIS CODE BLOCK

    dfs = {}
    for index, filename in enumerate(filenames):
      dfs[filename] = {}
      dfs[filename]['filename'] = '.'.join([filename, 'ph', 'csv'])
      identity = identifiers[index]
      # Create a regex pattern that joins the identifier with Boolean ORs
      # Also, make it so that it can be anywhere in the column name and be
      # included.
      pattern = f".*{'|'.join([list(df)[0], identity])}.*"
      # Only include relevant column, set row label as index, and drop any rows that have all missing values
      dfs[filename]['data'] = df.filter(regex = pattern).set_index(df.columns[0]).dropna(how = 'all')
      # Rename columns to omit location-year pairs
      dfs[filename]['data'].columns = [ trait_to_column(t) for t in dfs[filename]['data'].columns ]

    # Return the resultant dataframes
    return dfs

  except:
    raise 

  # In case something went wrong, return None and test for that on response
  return None
