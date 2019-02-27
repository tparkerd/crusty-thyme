"""
Unit tester module for verifying the output of the `splitLongFormat` module
Sample name of input file: `5.mergedWeightNorm.LM.rankAvg.longFormat.csv`
"""
import pytest
from lib.transformer.csv import process
from lib.helpers import Convert
import math

def test_csv(args_csv, data_csv):
  args = args_csv
  src_data = data_csv
  resultant_files = process(args)

  src_processed_count = 0
  target_processed_count = 0

  # Compare each value from source to targets
  # For each row...
  for row in src_data.itertuples(index = True):
    # For each column (get index and column name)
    for i, col in enumerate(src_data.columns.values):
      index_name = row[0]

      # Fetch names and values from source
      src_col_name = col
      src_value = row[i + 1]

      # For each value, translate the column as the filename, and use it to
      # to access the target file's data
      target_name = Convert.loyr_to_filename(Convert.trait_to_identifier(src_col_name))
      target_data = resultant_files[target_name]['data']

      # Fetch names and values from target file
      target_col_name = Convert.trait_to_column(src_col_name)
      
      # In case the source value is NAN, we need to make sure that there is not
      # an entry for the line in the target file. As such, the index for the
      # line should *not* be in the target file if there was no growout for said
      # line. However, if the line was part of the growout, but that value was
      # not measured, the value will be there, and it has to be checked for NAN
      if math.isnan(src_value):
        # Check that index is not in target dataframe
        if index_name in target_data.index:
          # Make sure that is is also NAN, otherwise we have an error
          target_value = target_data.loc[[index_name], [target_col_name]].values[0,0]
          src_processed_count = src_processed_count + 1 # Got to a valid comparison, so we can consider it processed
          assert math.isnan(target_value), f'Source value {target_value} is not considered NAN.'
        # Source NAN value was omitted from target file
        # Line was not present in growout (aka, location & year)
        else:
          pass
      else:
        src_processed_count = src_processed_count + 1 # Got to a valid comparison, so we can consider it processed
        target_value = target_data.loc[[index_name], [target_col_name]].values[0,0]
        assert math.isclose(src_value, target_value, rel_tol=1e-20), f'Values {src_value}, {target_value} are not close enough to be considered equal.'

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
        target_col_name = col
        target_value = row[i + 1]

        # For each value, translate the column name back to the original by
        # combining with the filename. Use it to access the source dataset
        src_col_name = Convert.column_to_trait(target_col_name, target_name)
        src_value = src_data.loc[[index_name], [src_col_name]].values[0,0]

        target_processed_count = target_processed_count + 1 # Got to a valid comparison, so we can consider it processed
        # Check for NANs, otherwise make sure the values are relatively equal
        if math.isnan(target_value):
          assert math.isnan(src_value), f'Source value {src_value} is not considered NAN.'
        else:
          assert math.isclose(target_value, src_value, rel_tol=1e-20), f'Values {target_value}, {src_value} are not close enough to be considered equal.'
        
  # Successfully processed from source > targets *and* targets > source
  # Check that the same number of values were compared
  difference = src_processed_count - target_processed_count
  assert src_processed_count == target_processed_count, f'The number of values processed for input files differed by {difference}'