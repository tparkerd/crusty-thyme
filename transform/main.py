"""Data Transformer Script

Example:
  ```bash
  python splitLongFormat.py -v input_file
  N files, M traits, P lines
  Line/Pedigree, Trait 1, Trait 2, Trait 3, Trait 4...Trait M
  Line 1, 1, 2, 3, 4, 5...M
  Line 2, 1, 2, 3, 4, 5...M
  ...
  Line P, 1, 2, 3, 4, 5...M
  ```

Background:
  Turns out the file that this was created for changed 

  TODO(timp): Take everything that isn't file specific out and put it into its
              module. Make separate files/modules with just functions that can 
              parse files and will be the 'versions' of transformers
"""

import argparse
import datetime
import importlib
import os
from pprint import pprint
from util import convert, helpers

def process(args):
  try:
    # Determine the type of transformer to use
    package_path = 'transform'
    directory = './transformer'
    transformers = set([ f[:-3] for f in os.listdir(directory) if not f.startswith('_') and f.endswith('.py') ])
    module_path = directory.replace('.', '').replace('/', '', 1).replace('/', '.')

    # Import the user-specified transformer if it exists
    if args.transformer not in transformers:
      if args.transformer is None:
        raise Exception("No transformer was supplied. Cannot process data. Aborting.")
      else:
        raise Exception("Unknown transformer. Aborting.")
    else:
      transformer = importlib.import_module(f'{package_path}.{module_path}.{args.transformer}')

    # Pass args to the chosen transformer and get back resultant data
    dfs = transformer.process(args)

    # Output the files
    if args.debug is False:
      try:
        if not os.path.exists(args.outdir):
          os.makedirs(args.outdir)
      except:
        raise
      for df in dfs.keys():
        if (args.verbose):
          pprint(dfs[df])
        dfs[df]['data'].to_csv(os.path.join(str(args.outdir), dfs[df]['filename']))
      pprint(f"Created {len(dfs.keys())} files in {args.outdir}")
    else:
      for df in dfs.keys():
        if (args.verbose):
          pprint(dfs[df])
      pprint(f"Output {len(dfs.keys())} datasets")

  except:
    raise 

def parseOptions():
  """
  Function to parse user-provided options from terminal
  """
  parser = argparse.ArgumentParser()
  parser.add_argument('files', metavar='FILE', nargs='*', help='Files to read. If empty, STDIN is used')
  parser.add_argument("--verbose", action="store_true", help="Increase output verbosity")
  parser.add_argument("-v", "--version", action="version", version='%(prog)s 1.0-alpha')
  parser.add_argument("-o", "--outdir", default = f"output_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}", help="Path of output directory")
  transformers = list(set([ f[:-3] for f in os.listdir('./transformer') if not f.startswith('_') and f.endswith('.py') ]))
  parser.add_argument("-t", "--transformer", default = None, help = f"Name of the format transformer to use. List of available transformers: {transformers}")
  parser.add_argument("--vcf_input", default = None, help = f"Path to the VCF file that contains genotype data for all chromosomes. Required for vcf_* transformers")
  parser.add_argument("--index", default = None, help = "NOT IMPLEMENTED. Name of the column for input")
  parser.add_argument("--debug", action = "store_true", help = "Enables --verbose and disables writes to disk")
  args = parser.parse_args()
  if args.debug is True:
    args.verbose = True
  
  return args

if __name__=="__main__":
  args = parseOptions()
  process(args)
