"""Common conversion methods for data transformations"""
import datetime
import fileinput
import math
import re

import pandas as pd


def expand_location_code(code):
  """
  Convert a location code (String) to its full name. The file `locations.csv`
  contains a dictionary of the key-value pairs. If original string is
  returned, check the `locations.csv` for its definition.

  Args:
    code (str): abbreviation for location

  Returns:
    str: Return full string of value if defined in locations dictionary, otherwise returns the original string value.

  Example:
    >>> expand_location_code('FL')
    'Florida'
    >>> expand_location_code('PU')
    'Purdue'

  """
  location_fp = "locations.csv"
  locations = pd.read_csv(location_fp, index_col=0)
  if code.upper() in locations.index:
    return locations.loc[code.upper()]["Name"]
  else:
    return code


def is_location_year(trait):
  """
  Determine if value is a (location code, year) pair

  Args:
    trait (str):

  Returns:
    bool: Return True if value is a valid (location, year) pair, False otherwise.

  Example:
    >>> is_location_year(FL06)
    True
    >>> is_location_year(FLA10)
    False
    >>> is_location_year(WR10)
    True
    >>> is_location_year(0242)
    False
    >>> is_location_year(FLAG)
    False

  """
  # If it's not four characters, it's not a location-year pair
  if len(trait) != 4:
    return False

  # If the last two characters are not integers, it's not a location-year pair
  if trait[-2:].isdigit() == False:
    return False

  # If the first two characters are not letters, it's not a location-year pair
  if trait[0:1].isalpha() == False:
    return False

  return True


def get_location_year(trait):
  """
  Determine if value is a (location code, year) pair

  Args:
    trait (str):

  Returns:
    tuple: tuple containing:

    * location (str): location code (unique value)
    * year (int): year

  Example:
    >>> get_location_year('FL06')
    ('FL', 2006)
    >>> get_location_year('FLA10')
    ('FL', 2010)
    >>> get_location_year('WR10')
    ('WR', 2010)
    >>> get_location_year('PU98')
    ('PU', 1998)
  """
  # Get the location and year from the last four characters
  location_code = trait[-4:-2]
  # When the last two digits of a year are larger than the current year,
  # then assume that the experiment was done in the 1900s
  year = None
  dd = datetime.datetime.strptime(trait[-2:], "%y").year
  if dd > datetime.datetime.now().year:
    year = dd.replace(year=dd - 100)
  else:
    year = dd

  if year is None:
    raise Exception(
      "Unable to convert `"
      + str(trait)
      + "` to location-year pair. <location_code: "
      + location_code
      + ", year: "
      + str(year)
      + ">"
    )

  return location_code, year


def loyr_to_filename(trait):
  """
  Extract the location and year from a trait

  Args:
    trait (str):

  Returns:
    str: Return a new string as the basename (without extension) of a filename

  Example:
    >>> loyr_to_filename('FL06')
    'FL_2006'
    >>> loyr_to_filename('FL10')
    'FL_2010'
    >>> loyr_to_filename('WR10')
    'WR_2010'
    >>> loyr_to_filename('PU98')
    'PU_1998'
  """
  trait_id = trait.split("_")[-1]

  # Check if the trait id is a location-year pair or otherwise
  # Set it's filename according to which identifier is used
  if is_location_year(trait_id):
    location, year = get_location_year(trait)
    trait_id = "_".join([location, str(year)]).strip()
  else:
    trait_id = trait_id.strip()

  return trait_id


def filename_to_loyr(filename):
  """
  Convert filename into a location year truncated string

  Args:
    trait (str):

  Returns:
    str: Return a new string as the basename (without extension) of a filename

  Example:
    >>> filename_to_loyr('FL_2006')
    'FL06'
    >>> filename_to_loyr('FL_2010')
    'FL10'
    >>> filename_to_loyr('WR_2010')
    'WR10'
    >>> filename_to_loyr('PU_1998')
    'PU98'
  """

  # Hardcoded length
  # NOTE(timp): There may need to be a different way of handling this
  #             Consider changing the LOYR references to growouts and then
  #             generalizing them.
  if len(filename) != 7:
    return filename

  # Check prefix (location) and suffix (year) are valid types
  try:
    prefix, suffix = filename.split("_")
    if not isinstance(prefix, str):
      raise Exception
    suffix = int(suffix)
    suffix = str(suffix)[-2:]
  except:
    raise

  # Combine the prefix and suffix, omitting leading two digits of year
  return f"{prefix}{suffix}"


def trait_to_identifier(trait):
  """Strip string of whitespace so that it can be used as an identifier to search the dataset with.

  Args:
    trait (str):

  Returns:
    str: Return a new string

  Example:
    >>> trait_to_identifier('FL06')
    'FL06'
    >>> trait_to_identifier('WR10\\n')
    'WR10'
    >>> trait_to_identifier('PU98\\r\\n')
    'PU98'

  """
  trait_id = trait.split("_")[-1]

  # Check if the trait id is a location-year pair or otherwise
  # Set it's filename according to which identifier is used
  if is_location_year(trait_id):
    trait_id = trait_id.strip()
  else:
    trait_id = trait_id.strip()

  return trait_id


def trait_to_column(trait):
  """Remove trailing location-year value from trait string.

  Args:
    trait (str):

  Returns:
    str: Return a new string

  Example:
    >>> trait_to_column('weight_FL06')
    'weight'
    >>> trait_to_column('B11_lmResid_MO06')
    'B11_lmResid'
  """
  result = "_".join(trait.split("_")[:-1])
  if result == "":  # in case of row label (left-most column label)
    return trait
  return result


def column_to_trait(column_name, filename):
  """Convert a short column name back into a long format trait

  Args:
    column_name (str): placeholder
    filename (str): placeholder

  Returns:
    str: Return a new string

  Example:
    >>> column_to_trait('weight', 'FL_2006')
    'weight_FL06'
    >>> column_to_trait('B11_lmResid', 'MO_2006')
    'B11_lmResid_MO06'
  """
  # Check for the type of column name
  # I.e., does it contain a LOYR pair
  candidate_loyr = f"{filename[:2]}{filename[-2:]}"
  if is_location_year(candidate_loyr):
    return f"{column_name}_{filename[:2]}{filename[-2:]}"
  else:
    return f"{column_name}_{filename}"

