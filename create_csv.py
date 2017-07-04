import sys
from celery import group
import lib.report_parsers as jcfg_report_parsers
import tasks
from os import walk
import gzip
import json
import pandas as pd
import numpy as np


def main(path):
    path = path + '/' if path[-1] != '/' else path
    (_, _, reports) = next(walk(path))
    BATCH_SIZE = 1000
    counter = 0
    batches = [reports[i:i+BATCH_SIZE] for i in range(0, len(reports), BATCH_SIZE)]
    out_file = 'data/peimphash.csv.gz'
    for idx, batch in enumerate(batches):
        jobs = group([tasks.extract_content.s('extract_peimphash', report, path) for report in batch])
        result = jobs.apply_async()
        result.join()
        arr = np.array(result.get())
        frame = pd.DataFrame(data=list(arr[:,1]), index=arr[:,0])
        frame.index.name = 'link'
        frame.columns = ['pe_imphash']
        frame.to_csv(path_or_buf='data/checkpoints/pe32_peimphash{}.csv.gz'.format(idx + 1), compression='gzip')


if __name__ == '__main__':
    main(sys.argv[1])
