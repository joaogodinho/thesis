"""
    Calculate the average percent of saved space
    by removing the whitespaces
"""

import gzip
import re
import sys
from os import walk

def main(data_dir):
    re_replace = re.compile(r'>\s+<', re.MULTILINE)
    re_replace2 = re.compile(r'\s{3,}', re.MULTILINE)
    (_, _, reports) = next(walk(data_dir))
    saved = 0

    data_dir = data_dir + '/' if data_dir[-1] != '/' else data_dir
    for report in map(lambda x: data_dir + x, reports):
        with gzip.open(report) as gz_file:
            content = gz_file.read().decode('utf8')
        before = len(content)
        content = re.sub(re_replace, '><', content)
        content = re.sub(re_replace2, '', content)
        after = len(content)
        saved += (before - after) / before

    saved = saved / len(reports)
    print('Saved average: {0:.3f}'.format(saved))

if __name__ == '__main__':
    main(sys.argv[1])
