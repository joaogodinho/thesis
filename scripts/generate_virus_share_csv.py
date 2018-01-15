"""
    Generate CSV with samples that are malware
    according to VirusShare
"""
import argparse
import pandas as pd
import os


def virus_share_generator(folder, reports, output):
    reports = pd.read_csv(reports, compression='gzip')
    reports = reports.set_index('link')
    links = []
    for file in os.listdir(folder):
        print('Checking in {}...'.format(file))
        with open(os.path.join(folder, file), 'r') as md5_file:
            md5s = filter(lambda x: x[0] != '#',
                          map(lambda x: x.strip(), md5_file.readlines()))
            links += list(reports[reports.md5.isin(md5s)].index.values)
    links = pd.DataFrame(links)
    links.to_csv(output, compression='gzip')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('virus_share_folder')
    parser.add_argument('reports_csv')
    parser.add_argument('output_csv')
    args = parser.parse_args()
    virus_share_generator(args.virus_share_folder, args.reports_csv, args.output_csv)