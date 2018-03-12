import gzip
from lxml import etree
import sys
import celery
import json


app = celery.Celery('tasks', backend='rpc://', broker='pyamqp://jcfg:jcfg@localhost/thesis')

@app.task
def file_info(report):
    """ Takes the sample information from the raw HTML.
    Returns a tuple with all the information
    """
    STR0 = '<section id="information">'
    STR1 = '<section id="file">'
    with gzip.open(report) as gzip_file:
        content = gzip_file.read().decode('utf8')

    result = dict()
    result['link'] = report

    doc = etree.HTML(content[content.find(STR0):])
    if doc is None:
        return result
    # Start time
    start_time = doc.xpath('//div[@class="box-content"]/table/tbody/tr/td[2]/text()')
    result['start_time'] = start_time[0] if len(start_time) >= 1 else None
    # End time
    end_time = doc.xpath('//div[@class="box-content"]/table/tbody/tr/td[3]/text()')
    result['end_time'] = end_time[0] if len(end_time) >= 1 else None

    # File name
    doc = etree.HTML(content[content.find(STR1):])
    file_name = doc.xpath('//div[@class="box-content"]/table/tr[1]/td[1]/text()')
    result['file_name'] = file_name[0] if len(file_name) >= 1 else None

    # File size
    file_size = doc.xpath('//div[@class="box-content"]/table/tr[2]/td[1]/text()')
    result['file_size'] = file_size[0].split(' ')[0] if len(file_size) >= 1 else None

    # File type
    file_type = doc.xpath('//div[@class="box-content"]/table/tr[3]/td[1]/text()')
    result['file_type'] = file_type[0] if len(file_type) >= 1 else None

    # MD5
    md5 = doc.xpath('//div[@class="box-content"]/table/tr[4]/td[1]/text()')
    result['md5'] = md5[0] if len(md5) >=1 else None

    # SHA1
    sha1 = doc.xpath('//div[@class="box-content"]/table/tr[5]/td[1]/text()')
    result['sha1'] = sha1[0] if len(sha1) >=1 else None

    # SHA256
    sha256 = doc.xpath('//div[@class="box-content"]/table/tr[6]/td[1]/text()')
    result['sha256'] = sha256[0] if len(sha256) >=1 else None

    # SHA512
    sha512 = doc.xpath('//div[@class="box-content"]/table/tr[7]/td[1]/text()')
    result['sha512'] = sha512[0] if len(sha512) >=1 else None

    # CRC32
    crc32 = doc.xpath('//div[@class="box-content"]/table/tr[8]/td[1]/text()')
    result['crc32'] = crc32[0] if len(crc32) >=1 else None

    # SSDeep
    ssdeep = doc.xpath('//div[@class="box-content"]/table/tr[9]/td[1]/text()')
    result['ssdeep'] = ssdeep[0] if len(ssdeep) >=1 else None

    return result


@app.task
def vendors_info(report):
    STR0 = '<section id="static_antivirus">'
    with gzip.open(report) as gzip_file:
        content = gzip_file.read().decode('utf8')

    doc = etree.HTML(content[content.find(STR0):])
    vendors = dict()
    vendors['link'] = report
    if doc is not None:
        rows = doc.xpath('//section[@id="static_antivirus"]/table/tr[position()>1]')
        for tr in rows:
            vendor = tr.xpath('td[1]/text()')
            sign = tr.xpath('td[2]/span/text()')
            if len(vendor) >= 1 and len(sign) >= 1:
                vendors[vendor[0]] = sign[0]
    return vendors


@app.task
def report_imports(report):
    STR0 = '<div id="pe_imports">'
    with gzip.open(report) as gzip_file:
        content = gzip_file.read().decode('utf8')

    result = dict()
    result['link'] = report
    doc = etree.HTML(content[content.find(STR0):])
    if doc is not None:
        dlls = doc.xpath('//div/div/div/strong/text()')
        dlls = ';'.join(sorted(set(map(lambda x: x.split(' ')[1], dlls))))
        result['imports'] = dlls
    return result


@app.task
def behavior_categories(report):
    STR0 = '<div id="graph_process_details">'
    STR1 = '<script type="text/javascript">'
    STR2 = 'var graph_raw_data = '
    STR3 = '</script>'
    with gzip.open(report) as gzip_file:
        content = gzip_file.read().decode('utf8')

    result = dict()
    result['link'] = report

    # Use specific strings to find the dynamic calls,
    # as sometimes the file is too big for etree
    content = content[content.find(STR0):]
    content = content[content.find(STR1) + len(STR1):].replace(STR2, '')
    content = content[:content.find(STR3)]
    content = content.strip()[:-1] # -1 removes ending ';'
    if content is not None and len(content) != 0:
        try:
            processes = json.loads(content)
        except:
            print(report)
            raise
        # Get only the categories
        for proc in processes:
            for call in proc['calls']:
                result[call['category']] = result.setdefault(call['category'], 0) + 1
    return result


@app.task
def behavior_func_calls(report):
    STR0 = '<div id="graph_process_details">'
    STR1 = '<script type="text/javascript">'
    STR2 = 'var graph_raw_data = '
    STR3 = '</script>'
    with gzip.open(report) as gzip_file:
        content = gzip_file.read().decode('utf8')

    result = dict()
    result['link'] = report

    # Use specific strings to find the dynamic calls,
    # as sometimes the file is too big for etree
    content = content[content.find(STR0):]
    content = content[content.find(STR1) + len(STR1):].replace(STR2, '')
    content = content[:content.find(STR3)]
    content = content.strip()[:-1] # -1 removes ending ';'
    if content is not None and len(content) != 0:
        try:
            processes = json.loads(content)
        except:
            print(report)
            raise
        # Get only the categories
        for proc in processes:
            for call in proc['calls']:
                result[call['api']] = result.setdefault(call['api'], 0) + 1
    return result
