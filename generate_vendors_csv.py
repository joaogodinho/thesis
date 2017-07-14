"""
    Generates the vendors.csv file with:
        link,
"""
import sys
import tasks
from os import walk
from celery import group
import numpy as np
import pandas as pd


def main(reports, folder, out):
    BATCH_SIZE = 10000
    base_file = 'reports.csv.gz'
    filename = 'vendors.csv.gz'
    folder = folder + '/' if folder[-1] != '/' else folder
    out = out + '/' if out[-1] != '/' else out

    reports = pd.read_csv(reports)
    reports = reports.link
    batches = [reports[i:i+BATCH_SIZE] for i in range(0, len(reports), BATCH_SIZE)]
    for idx, batch in enumerate(batches):
        # Send the messages
        jobs = group([tasks.extract_report_vendors.s(report, folder) for report in batch])
        result = jobs.apply_async()
        result.join()
        arr = np.array(result.get())
        # Transform the results into a dataframe
        frame = pd.DataFrame(data=list(arr[:,1]), index=arr[:,0])
        frame.index.name = 'link'
        frame.to_csv(path_or_buf=out + 'temp{}.csv'.format(idx + 1), compression='gzip')

    # Join all checkpoints into final CSV
    (_, _, checkpoints) = next(walk(out))
    concatenated_result = []
    for c in checkpoints:
        concatenated_result.append(pd.read_csv(out + c, compression='gzip'))
    final_frame = pd.concat(concatenated_result)
    final_frame = final_frame.set_index('link')
    final_frame.to_csv(path_or_buf=out + '../' + filename, compression='gzip')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
