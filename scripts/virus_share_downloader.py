"""
    Simple script to download virus share hashes
"""
import argparse
import gevent
import gevent.pool
from gevent import monkey; monkey.patch_all()
from urllib.request import urlretrieve


def gevent_func(pair):
    print('Fetching {}...'.format(pair[0]))
    urlretrieve(pair[0], pair[1])

def downloader(destination_dir):
    # https://virusshare.com/hashes/VirusShare_00000.md5
    base_url = 'https://virusshare.com/hashes/'
    file_name = 'VirusShare_{}.md5'
    # As of 22/10/17; + 1 due to 0 based
    total_files = 296 + 1

    # Append / if missing
    destination_dir = destination_dir + '/' if destination_dir[-1] != '/' else destination_dir

    # Generate (URL, filename) list
    url_list = []
    for i in range(total_files):
        name = file_name.format(str(i).rjust(5, '0'))
        url = base_url + name
        filename = destination_dir + name
        url_list.append((url, filename))

    # 10 Concurrent downloads
    pool = gevent.pool.Pool(10)
    jobs = [pool.spawn(gevent_func, i) for i in url_list]
    gevent.joinall(jobs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('destination_dir')
    args = parser.parse_args()
    downloader(args.destination_dir)
