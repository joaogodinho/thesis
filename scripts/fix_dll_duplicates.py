"""
    Fixes duplicates on the DLLs files
"""
import argparse
import pandas as pd


def fixer_func(dlls):
    """
        Removes duplicated dll entries and sorts dlls
    """
    if type(dlls) is str:
        return ';'.join(sorted(set(dlls.split(';'))))
    return dlls


def dll_fixer(input_csv, output_csv):
    """
        Main function
    """
    dframe = pd.read_csv(input_csv)
    dframe = dframe.set_index('link')
    # Apply function
    dframe.dlls = dframe.dlls.map(fixer_func)
    # Save again
    dframe.to_csv(output_csv, compression='gzip')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_csv')
    parser.add_argument('output_csv')
    args = parser.parse_args()
    dll_fixer(args.input_csv, args.output_csv)