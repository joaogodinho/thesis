import sys
from celery import group
import lib.report_parsers as jcfg_report_parsers
import tasks
from os import walk
import pandas as pd
import numpy as np
"""
    Creates the CSV for the vendors classification
    The CSV contains the link and vendors and their classification
"""


def main(path, outpath):
    BATCH_SIZE = 10000
    BATCH_SIZE = 100
    path = path + '/' if path[-1] != '/' else path
    outpath = outpath + '/' if outpath[-1] != '/' else outpath

    (_, _, reports) = next(walk(path))
    # Split the reports into batches, which will then be saved as checkpoints
    batches = [reports[i:i+BATCH_SIZE] for i in range(0, len(reports), BATCH_SIZE)]
    for idx, batch in enumerate(batches):
        # Send the messages
        jobs = group([tasks.extract_content.s('extract_antivirus', report, path) for report in batch])
        result = jobs.apply_async()
        result.join()
        arr = np.array(result.get())
        print(len(arr))
        counter = 0
        for r in arr:
            if r[1] is None:
                print(r)
                counter += 1
        print(counter)
        arr = arr[np.where(arr[:,1] != np.array(None))]
        print(len(arr))
        # Transform the results into a dataframe
        frame = pd.DataFrame(data=list(arr[:,1]), index=arr[:,0])
        frame.index.name = 'link'
        frame.to_csv(path_or_buf=outpath + 'pe32_vendors{}.csv.gz'.format(idx + 1), compression='gzip')
        break

    (_, _, checkpoints) = next(walk(outpath))
    concatenated_result = []
    for c in filter(lambda x: 'vendors' in x, checkpoints):
        concatenated_result.append(pd.read_csv(outpath + c))
    final_frame = pd.concat(concatenated_result)
    final_frame = final_frame.set_index('link')
    final_frame.to_csv(path_or_buf=outpath + 'pe32_vendors.csv.gz', compression='gzip')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
