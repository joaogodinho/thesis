import sys
from celery import group
import lib.report_parsers as jcfg_report_parsers
import tasks
from os import walk
import time
import gzip
import json


def main(input_dir, output_dir, gig):
    # Read around 10GB to memory
    # CONTENT_SIZE = 1000000 * 1000 * gig
    # content_size = 0
    # content_batch = []
    data_dir = input_dir + '/' if input_dir[-1] != '/' else input_dir
    output = output_dir + '/' if output_dir[-1] != '/' else output_dir
    (_, _, samples) = next(walk(input_dir))

    counter = 0
    for sample in samples:
        tasks.extract_from_report.delay(sample, data_dir, output)
        counter += 1
        if counter == 1000:
            time.sleep(20)
            counter = 0
        # jobs = group
        # with gzip.open(data_dir + sample) as gz_file:
        #     content = jcfg_report_parsers.remove_whitespaces(gz_file.read().decode('utf8'))
        #     content_size += len(content)
        #     content_batch.append((sample, content))
        #     if content_size >= CONTENT_SIZE:
        #         print('Parsing {0} bytes of files'.format(content_size))
        #         # Fire away
        #         jobs = group([tasks.extract_from_report.s(link, content) for link, content in content_batch])
        #         # Wait for workers to finish
        #         result = jobs.apply_async()
        #         result.join()
        #         for r in result.get():
        #             with open(output + r[0], 'w') as file:
        #                 file.write(json.dumps(r[1]))
        #         content_size = 0
        #         content_batch = []

    # print('Parsing last {0} bytes of files'.format(content_size))
    # # Fire away
    # jobs = group([tasks.extract_from_report.s(link, content) for link, content in content_batch])
    # # Wait for workers to finish
    # result = jobs.apply_async()
    # result.join()
    # for r in result.get():
    #     with open(output + r[0], 'w') as file:
    #         file.write(json.dumps(r[1]))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]))
