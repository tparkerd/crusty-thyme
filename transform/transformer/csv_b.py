"""
CSV Dataset Transformer B

This is the original transformer that was meant to transform the long format of
traits by line, where the trait contains location and year. It splits a single
file into N files, where N is the number of location and year combinations.

TL;DR: Generates a phenotype files for each growout.

Expected input:
  N files, M traits, P lines
  Line/Pedigree, Trait 1_LOYR, Trait 2_LOYR, Trait 3_LOYR, ...Trait M_LOYR
  Line 1, 1, 2, 3, 4, 5...M
  Line 2, 1, 2, 3, 4, 5...M
  ...
  Line P, 1, 2, 3, 4, 5...M


Expected input file: 5.mergedWeightNorm.LM.rankAvg.longFormat.csv
  Pedigree                    weight_FL06   weight_MO06   weight_NC06   weight_NY06 ...
  282set_33-16                299.8285      NA            247.08025     144.066125
  282set_38-11Goodman-Buckler NA            157.62175   	183.5531625  	NA
  282set_4226                 NA	          NA          	266.214     	NA
  282set_4722                 155.593625	  130.501625  	98.497      	159.30275
  282set_A188                 252.62675	    255.4635    	213.556125  	236.02
  ...

Expected output format:
  Pedigree    	  weight    	B11_lmResid 	  Na23_lmResid	  Mg25_lmResid ...
  282set_33-16	  299.8285    -5.430818189	  1.700641336	    -1604.177087
  282set_4722 	  155.593625  -5.543528111	  3.805945098	    -329.6907951
  282set_A188 	  252.62675   -0.713238648	  1.672346299	    368.6371063
  282set_A272 	  152.31975   20.80615839	    -6.553397553	  329.4494714
  282set_A441-5	  329.83625   -4.609531942	  -12.93404438	  884.6418555
  ...

Example output file list:
  FL_2006.ph.csv
  MO_2006.ph.csv
  NC_2006.ph.csv
  NY_2006.ph.csv
  NY_2010.ph.csv
  PR_2006.ph.csv
  PU_2009.ph.csv
  PU_2010.ph.csv
  rankAvg.ph.csv
  SA_2006.ph.csv


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
      filename = loyr_to_filename(trait)
      filenames.add(filename)
      identity = trait_to_identifier(trait)
      identifiers.add(identity)
    filenames = sorted(list(filenames))
    identifiers = sorted(list(identifiers))

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
