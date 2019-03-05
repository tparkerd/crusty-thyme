"""
Helper Functions for data transformation script
"""

import datetime
import pandas as pd
import fileinput
import re
import math

def read_stdin(fp, delimiter):
  """
  Function that handles any textual data streamed in from stdin

  Args:
    fp (FileInupt): list of filenames
    delimiter (str): value to split data

  Returns:
    pandas.DataFrame: placeholder
  """
  data = []
  header = [ column.strip() for column in fp.readline().split(delimiter) ]
  typings = None
  for line in fp:
    line = [ cell.strip() for cell in line.split(delimiter) ]
    # Covert strings of numeric values to numeric type
    for index, value in enumerate(line):
      # Check if it's an integer, float, or some variation of NA(N)
      if re.compile(r'(^\-?\d+(.?\d+)?$)|(^[nN][aA][nN]?)$').search(value):
        if 'na' in value.lower():
          line[index] =  math.nan
        else:
          try:
            line[index] = float(value)
          except ValueError:
            print (f'`{str(value)}` cannot be cast as float.')
    # Verify that the current row has the same typings as previous row
    # CASE: Typings have not been established
    if typings is None:
      typings = [ type(cell) for cell in line ]
    else:
      try:
        for index, value in enumerate(line):
          if not isinstance(value, typings[index]):
            raise TypeError(f"`{value}` does not match column type of {typings[index]}. Check for extra headers or comments.")

      except:
        raise
    data.append(line)

  df = pd.DataFrame.from_records(data, columns = header)
  return df

def read_files(fp, delimiter):
  """
  Reads contents of a CSV file and creates a dataframe of it

  Args:
    fp (FileInput): list of filenames
    delimiter (str): value to split data

  Returns:
    pandas.DataFrame: placeholder
  """
  # Fill an empty dataframe with all the possible traits and lines
  df = pd.DataFrame()
  for line in fp:
    # Float precision helps to avoid rounding errors, but it does hurt performance
    df = pd.concat([df, pd.read_table(fp.filename(),
                    float_precision='round_trip', delimiter = delimiter)], axis = 0,
                    ignore_index = True, sort = False)
    fp.nextfile()
  return df

def read_data(args, delimiter):
  """Reads in the data from either STDIN or a list of files

  Args:
    args (Namespace): arguments supplied by user
  
  Returns:
    Pandas DataFrame: placeholder
  """
  files = args.files
  try:
    fp = fileinput.input(files)
    df = None
    if len(files) < 1:
      df = read_stdin(fp, delimiter)
    else:
      df = read_files(fp, delimiter)

    if df is None:
      raise Exception("No data supplied.")
  except:
    raise

  return df