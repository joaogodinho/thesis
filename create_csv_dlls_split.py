import sys
from celery import group
import lib.report_parsers as jcfg_report_parsers
import tasks
from os import walk
import pandas as pd
import numpy as np
"""
    Creates a CSV for each possible DLL
    Each CSV contains the link and list of used imports
"""


def main(csv_file, path, dlls_file, outpath):
    BATCH_SIZE = 10000
    path = path + '/' if path[-1] != '/' else path
    outpath = outpath + '/' if outpath[-1] != '/' else outpath

    # Get all used dlls
    with open(dlls_file, 'r') as file:
        dlls = map(str.strip, file.readlines())

    dlls_frame = pd.read_csv(csv_file)
    for dll in dlls:
        reports = dlls_frame[dlls_frame.dlls.str.contains(dll, regex=False)].link.values
        # Split the reports into batches, which will then be saved as checkpoints
        batches = [reports[i:i+BATCH_SIZE] for i in range(0, len(reports), BATCH_SIZE)]
        for idx, batch in enumerate(batches):
            # Send the messages
            jobs = group([tasks.extract_dlls_split.s(report, path, dll) for report in batch])
            result = jobs.apply_async()
            result.join()
            arr = np.array(result.get())
            # Transform the results into a dataframe
            frame = pd.DataFrame(data=list(arr[:,1]), index=arr[:,0])
            frame.index.name = 'link'
            frame.columns = [dll]
            frame.to_csv(path_or_buf=outpath + 'pe32_pedll-{}_{}.csv.gz'.format(dll, idx + 1), compression='gzip')

    (_, _, checkpoints) = next(walk(outpath))
    for dll in dlls:
        concatenated_result = []
        for c in filter(lambda x: x.contains(dll), checkpoints):
            concatenated_result.append(pd.read_csv(outpath + c))
            final_frame = pd.concat(concatenated_result)
            final_frame = final_frame.set_index('link')
            final_frame.to_csv(path_or_buf=outpath + 'pe32_pedll_{}.csv.gz'.format(dll), compression='gzip')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
