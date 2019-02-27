"""
CSV Dataset Transformer A

Transform the long format of traits by line, where the trait contains location
and year. It splits a single file into N files, where N is the number of
location and year combinations.

Expected input:
  N files, M traits, P lines
  Line/Pedigree, LocationYear 4-tuple,  Trait 1, Trait 2, Trait 3, ...Trait M
  Line 1, 1, 2, 3, 4, 5...M
  Line 2, 1, 2, 3, 4, 5...M
  ...
  Line P, 1, 2, 3, 4, 5...M

"""

import fileinput

import pandas as pd

from ..helpers import Convert, read_data


def process(args, delimiter = ','):
  """
  Process data

  Args:
    args (Namespace): arguments supplied by user
    delimiter (String): value to split data, default ','
  """
  try:
    df = read_data(args, delimiter)

    # The location column contains the LOYR (location, year) value
    # Get unique values in "loc" column, convert to filename
    identifiers = df['loc'].unique()

    dfs = {}
    for identity in identifiers:
      filename = Convert.loyr_to_filename(identity)
      dfs[filename] = {}
      dfs[filename]['filename'] = f'{filename}.csv'
      # For each identifier, create a new df that filters for rows with the
      # identifier
      # Select rows where loc == location, year pair
      dfs[filename]['data'] = df.loc[df['loc'] == identity]
      # Remove 'loc' column
      dfs[filename]['data'] = dfs[filename]['data'].drop(['loc'], axis = 1)
      # Set first column as index
      dfs[filename]['data'] = dfs[filename]['data'].set_index(df.columns[0])

    # Return the resultant dataframes
    return dfs

  except:
    raise 

  # In case something went wrong, return None and test for that on response
  return None
