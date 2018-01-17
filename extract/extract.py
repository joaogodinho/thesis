import pandas as pd
import argparse
import sys
import os
import celery
import logging
import tasks


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(asctime)s %(message)s')
logger = logging.getLogger("")
logger.setLevel(logging.INFO)


def splitter(l, n):
    """ Splits a list into chunks of
    n size, returns an iterator
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]


def main(function, pe32_file, samples_folder, output):
    pe32 = pd.read_csv(pe32_file)
    samples_folder = samples_folder + '/' if samples_folder[-1] != '/' else samples_folder 
    
    logger.info('Extracting {} from {} samples...'.format(function, len(pe32)))
    
    samples = list(map(lambda x: samples_folder + x, pe32.link.values))
    results = []

    for subset in splitter(samples, 1000):
        # Send task
        logger.info('Sending tasks...')
        jobs = celery.group([getattr(tasks, function).s(s) for s in subset])
        logger.info('Waiting...')
        result = jobs.apply_async()
        result.join()
        results += result.get()

    logger.info('Joining results to DataFrame')
    samples_info = pd.DataFrame(results)
    samples_info.link = samples_info.link.apply(lambda x: x.split('/')[4])
    samples_info = samples_info.set_index('link')
    samples_info.to_csv(output, compression='gzip')


if __name__ == '__main__':
    # Task to call, pe32 samples, samples folder, output file
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])