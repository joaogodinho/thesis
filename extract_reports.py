import sys
import lib.report_parsers as jcfg_report_parsers
import tasks
from os import walk
import time


def main(input_dir, output_dir):
    # Read around 10GB to memory
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

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
