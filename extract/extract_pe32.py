import pandas as pd
import argparse
import sys
import os


def main(headers, output, samples_folder):
    """ Takes the headers file and extracts samples
    that are PE32 into the output file. Makes sure
    samples are available.
    The output file contains the analysis ID and MD5
    """
    samples_folder = samples_folder + '/' if samples_folder[-1] != '/' else samples_folder 
    (_, _, samples) = next(os.walk(samples_folder))
    headers = pd.read_csv(headers)
    headers.file_type = headers.file_type.astype(str)
    headers = headers[headers.file_type.str.startswith('PE32 ')]
    headers.link = headers.link.apply(lambda x: x.split('/')[2])
    headers = headers[['link', 'md5']]
    headers = headers[headers.link.isin(samples)]
    headers = headers.set_index('link')
    headers.to_csv(output, compression='gzip')
    print('Extracted {} samples to {}.'.format(len(headers), output))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
