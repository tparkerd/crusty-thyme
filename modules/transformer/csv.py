"""
CSV Dataset Transformer

This is the original transformer that was meant to transform the long format of
traits by line, where the trait contains location and year. It splits a single
file into N files, where N is the number of location and year combinations.

Expected input:
  N files, M traits, P lines
  Line/Pedigree, Trait 1_LOYR, Trait 2_LOYR, Trait 3_LOYR, ...Trait M_LOYR
  Line 1, 1, 2, 3, 4, 5...M
  Line 2, 1, 2, 3, 4, 5...M
  ...
  Line P, 1, 2, 3, 4, 5...M

"""

import fileinput

import pandas as pd

from ..helpers import Convert, read_data


def process(args, delimiter = ','):
  """Process data

  Args:
    args (Namespace): arguments supplied by user
    delimiter (String): value to split data, default ','
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
      filename = Convert.loyr_to_filename(trait)
      filenames.add(filename)
      identity = Convert.trait_to_identifier(trait)
      identifiers.add(identity)
    filenames = sorted(list(filenames))
    identifiers = sorted(list(identifiers))

    dfs = {}
    for index, filename in enumerate(filenames):
      dfs[filename] = {}
      dfs[filename]['filename'] = '.'.join([filename, 'csv'])
      identity = identifiers[index]
      # Create a regex pattern that joins the identifier with Boolean ORs
      # Also, make it so that it can be anywhere in the column name and be
      # included.
      pattern = f".*{'|'.join([list(df)[0], identity])}.*"
      # Only include relevant column, set row label as index, and drop any rows that have all missing values
      dfs[filename]['data'] = df.filter(regex = pattern).set_index(df.columns[0]).dropna(how = 'all')
      # Rename columns to omit location-year pairs
      dfs[filename]['data'].columns = [ Convert.trait_to_column(t) for t in dfs[filename]['data'].columns ]

    # Return the resultant dataframes
    return dfs

  except:
    raise 

  # In case something went wrong, return None and test for that on response
  return None
