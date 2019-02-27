"""
Unit tester module for verifying the output of the CSV-A module
Sample name of input file: `1.meanByLineandLoc.divpanel.LocSpecificResids.csv`
"""
import pytest
from lib.transformer.csv_a import process
from lib.helpers import Convert
import math

def test_csv_a(args_csv_a, data_csv_a):
  args = args_csv_a
  src_data = data_csv_a
  resultant_files = process(args)

  src_processed_count = 0
  target_processed_count = 0

  # Compare each value from source to targets
  # For each row...
  for row in src_data.itertuples(index = True):
    index_name = row[0]
    target_name = row.loc
    # For each column (get index and column name)
    for i, col in enumerate(src_data.columns.values):
      # Fetch names and values from source
      src_value = row[i + 1]

      # Skip for non-numeric values
      # TODO: Rework so that the data isn't assumed to be numeric
      if not isinstance(src_value, float):
        continue

      # For each value, translate the column as the filename, and use it to
      # to access the target file's data
      target_data = resultant_files[Convert.loyr_to_filename(target_name)]['data']

      # In case the source value is NAN, we need to make sure that there is not
      # an entry for the line in the target file. As such, the index for the
      # line should *not* be in the target file if there was no growout for said
      # line. However, if the line was part of the growout, but that value was
      # not measured, the value will be there, and it has to be checked for NAN
      if math.isnan(src_value):
        # Check that index is not in target dataframe
        if index_name in target_data.index[1:]:
          # Make sure that is is also NAN, otherwise we have an error
          target_value = target_data.loc[[index_name], [col]].values[0,0]
          src_processed_count = src_processed_count + 1 # Got to a valid comparison, so we can consider it processed
          assert math.isnan(target_value), f'Source value {target_value} is not considered NAN.'
        # Source NAN value was omitted from target file
        # Line was not present in growout (aka, location & year)
        else:
          pass
      else:
        target_value = target_data.loc[[index_name], [col]].values[0,0]
        src_processed_count = src_processed_count + 1 # Got to a valid comparison, so we can consider it processed
        assert math.isclose(src_value, target_value, rel_tol=1e-20), f'Values {src_value}, {target_value} are not close enough to be considered equal. (i: {index_name}, fp: {target_name}, col: {col})'

  # Compare each value from targets to source
  # For each target file...
  for target_file in resultant_files:
    target_data = resultant_files[target_file]['data']
    target_name = resultant_files[target_file]['filename'][:-4]
    # For each row...
    for row in target_data.itertuples(index = True):
      # For each column (get index and column name)
      for i, col in enumerate(target_data.columns.values):
        index_name = row[0]

        # Fetch names and value from target
        target_value = row[i + 1]

        # Fetch the value from source
        # Filter the source data to only include values from a specific growout (LOYR)

        # converted = src_data.loc[[index_name],['loc']].values[0,0]
        filtered_src_data = src_data[src_data['loc'] == Convert.filename_to_loyr(target_name)]
        src_value = filtered_src_data.loc[[index_name], [col]].values[0,0]

        target_processed_count = target_processed_count + 1 # Got to a valid comparison, so we can consider it processed
        # Check for NANs, otherwise make sure the values are relatively equal
        if math.isnan(target_value):
          assert math.isnan(src_value), f'Source value {src_value} is not considered NAN.'
        else:
          assert math.isclose(target_value, src_value, rel_tol=1e-20), f'Values {target_value}, {src_value} are not close enough to be considered equal. (i: {index_name}, fp: {target_name}, col: {col})'
        
  # Successfully processed from source > targets *and* targets > source
  # Check that the same number of values were compared
  difference = src_processed_count - target_processed_count
  assert src_processed_count == target_processed_count, f'The number of values processed for input files differed by {difference}'