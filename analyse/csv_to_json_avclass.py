import pandas as pd
import sys
import numpy as np
import json


def main(file_info, vendors):
    file_info = pd.read_csv(file_info).set_index('link')

    vendors = pd.read_csv(vendors, dtype=str).set_index('link')
    vendors.replace('Clean', np.nan, inplace=True)
    vendors.dropna(how='all', inplace=True)

    file_info_vendors = file_info.join(vendors, how='inner')
    file_info_vendors.drop(['sha512', 'file_type',
                            'end_time', 'file_name', 'crc32', 'ssdeep', 'file_size'],
                           axis=1, inplace=True)

    # Samples that don't exist anymore
    file_info_vendors.dropna(subset=['md5'], inplace=True)
    file_info_vendors.start_time = pd.to_datetime(file_info_vendors.start_time, infer_datetime_format=True)
    unique_samples = file_info_vendors.sort_values(by='start_time').drop_duplicates(subset='md5', keep='last')

    output = ''
    for link, sample in unique_samples.iterrows():
        sample = sample.dropna()
        vendors = sample.drop(['md5', 'start_time'])

        out = dict()
        out['md5'] = sample['md5']
        out['sha1'] = sample['sha1']
        out['sha256'] = sample['sha256']
        out['av_labels'] = list(vendors.to_dict().items())

        output += json.dumps(out) + '\n'

    print(output)


if __name__ == '__main__':
    # file info, vendors
    main(sys.argv[1], sys.argv[2])