"""
    Generates the reports.csv file with:
        link, md5, date (w/ time), file_type, file_name
"""
import sys
import tasks
from os import walk
from celery import group
import numpy as np
import pandas as pd


def main(folder, out):
    BATCH_SIZE = 10000
    BATCH_SIZE = 4
    filename = 'reports.csv'
    folder = folder + '/' if folder[-1] != '/' else folder
    out = out + '/' if out[-1] != '/' else out

    (_, _, reports) = next(walk(folder))
    batches = [reports[i:i+BATCH_SIZE] for i in range(0, len(reports), BATCH_SIZE)]
    for idx, batch in enumerate(batches):
        # Send the messages
        jobs = group([tasks.extract_report_basic.s(report, folder) for report in batch])
        result = jobs.apply_async()
        result.join()
        arr = np.array(result.get())
        # Transform the results into a dataframe
        frame = pd.DataFrame(data=arr[:,range(1,5)], index=arr[:,0])
        frame.index.name = 'link'
        frame.columns = ['date', 'file_name', 'file_size', 'file_type']
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
    main(sys.argv[1], sys.argv[2])
