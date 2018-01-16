import pandas as pd
import argparse
import sys
import os
import gevent
import gevent.pool
import gzip
from lxml import etree
from gevent import monkey; monkey.patch_all()


def gevent_func(report):
    """ Takes the sample information from the raw HTML.
    Returns a tuple with all the information
    """
    STR0 = '<section id="information">'
    STR1 = '<section id="file">'
    with gzip.open(report) as gzip_file:
        content = gzip_file.read().decode('utf8')

    doc = etree.HTML(content[content.find(STR0):])
    if doc is None:
        return (report, None, None, None, None, None, None, None, None, None, None, None)
    # Start time
    start_time = doc.xpath('//div[@class="box-content"]/table/tbody/tr/td[2]/text()')
    start_time = start_time[0] if len(start_time) >= 1 else None
    # End time
    end_time = doc.xpath('//div[@class="box-content"]/table/tbody/tr/td[3]/text()')
    end_time = end_time[0] if len(end_time) >= 1 else None

    # File name
    doc = etree.HTML(content[content.find(STR1):])
    file_name = doc.xpath('//div[@class="box-content"]/table/tr[1]/td[1]/text()')
    file_name = file_name[0] if len(file_name) >= 1 else None

    # File size
    file_size = doc.xpath('//div[@class="box-content"]/table/tr[2]/td[1]/text()')
    file_size = file_size[0].split(' ')[0] if len(file_size) >= 1 else None

    # File type
    file_type = doc.xpath('//div[@class="box-content"]/table/tr[3]/td[1]/text()')
    file_type = file_type[0] if len(file_type) >= 1 else None

    # MD5
    md5 = doc.xpath('//div[@class="box-content"]/table/tr[4]/td[1]/text()')
    md5 = md5[0] if len(md5) >=1 else None

    # SHA1
    sha1 = doc.xpath('//div[@class="box-content"]/table/tr[5]/td[1]/text()')
    sha1 = sha1[0] if len(sha1) >=1 else None

    # SHA256
    sha256 = doc.xpath('//div[@class="box-content"]/table/tr[6]/td[1]/text()')
    sha256 = sha256[0] if len(sha256) >=1 else None

    # SHA512
    sha512 = doc.xpath('//div[@class="box-content"]/table/tr[7]/td[1]/text()')
    sha512 = sha512[0] if len(sha512) >=1 else None

    # CRC32
    crc32 = doc.xpath('//div[@class="box-content"]/table/tr[8]/td[1]/text()')
    crc32 = crc32[0] if len(crc32) >=1 else None

    # SSDeep
    ssdeep = doc.xpath('//div[@class="box-content"]/table/tr[9]/td[1]/text()')
    ssdeep= ssdeep[0] if len(ssdeep) >=1 else None

    return (report, md5, sha1, sha256, sha512, crc32, ssdeep, start_time, end_time, file_name, file_size, file_type)


def main(pe32_file, samples_folder, output):
    pe32 = pd.read_csv(pe32_file)
    samples_folder = samples_folder + '/' if samples_folder[-1] != '/' else samples_folder 
    
    print('Extracting info from {} samples...'.format(len(pe32)))
    
    samples = list(map(lambda x: samples_folder + x, pe32.link.values))

    # 1000 Concurrent jobs
    pool = gevent.pool.Pool(1000)
    jobs = [pool.spawn(gevent_func, i) for i in samples]
    print('Done spawning, waiting...')
    gevent.joinall(jobs)
    samples_info = pd.DataFrame([j.value for j in jobs], columns=['link', 'md5', 'sha1', 'sha256', 'sha512', 'crc32', 'ssdeep',
        'start_time', 'end_time', 'file_name', 'file_size', 'file_type'])
    samples_info.link = samples_info.link.apply(lambda x: x.split('/')[4])
    samples_info = samples_info.set_index('link')
    samples_info.to_csv(output, compression='gzip')



if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])