"""
    Filter for NSRL dataset.
    Extracts MD5 from software made by Microsoft and for Windows
"""
import sys
import argparse
import gevent
import gevent.pool
import pandas as pd
from gevent import monkey; monkey.patch_all()


def gevent_func(line, prod_code, op_code):
    # NSRLFile header
    #          ***                                 ***********   ************
    # "SHA-1","MD5","CRC32","FileName","FileSize","ProductCode","OpSystemCode","SpecialCode"
    line = list(map(lambda x: x.replace('"', ''), line.split(',')))
    if int(line[-3]) in prod_code: # and int(line[-2]) in op_code:
        return line[1]
    return False


def filtering(nsrl_dir, output_file):
    nsrl_dir = nsrl_dir + '/' if nsrl_dir[-1] != '/' else nsrl_dir
    manufacturers_file = nsrl_dir + 'NSRLMfg.txt'
    os_file = nsrl_dir + 'NSRLOS.txt'
    apptypes_file = nsrl_dir + 'NSRLProd.txt'
    files_file = nsrl_dir + 'NSRLFile.txt'

    # Load small files first
    manufacturers = pd.read_csv(manufacturers_file, encoding='ISO-8859-1')
    oses = pd.read_csv(os_file, encoding='ISO-8859-1')
    apptypes = pd.read_csv(apptypes_file, encoding='ISO-8859-1')

    # Filter Microsoft manufacturer and Windows OS
    microsoft_mfg = manufacturers[manufacturers.MfgName.str.contains('Microsoft')].MfgCode.values
    microsoft_oses = oses[oses.MfgCode.isin(microsoft_mfg) & oses.OpSystemName.str.contains('Windows')].OpSystemCode.values
    microsoft_apps = apptypes[apptypes.OpSystemCode.isin(microsoft_oses) & apptypes.MfgCode.isin(microsoft_mfg)].ProductCode.values

    with open(files_file, 'r', encoding='ISO-8859-1') as files:
        lines = files.readlines()
    pool = gevent.pool.Pool(10000)
    md5s = set()
    for i in range(int(len(lines) / 10000)):
        sys.stdout.write('Doing run #{} of {}\r'.format(i, int(len(lines) / 10000)))
        sys.stdout.flush()
        jobs = [pool.spawn(gevent_func, l, microsoft_apps, microsoft_oses) for l in lines[1+i:i+10000]]
        gevent.joinall(jobs)
        md5s.update([job.value for job in jobs if job.value != False])

    md5s = pd.DataFrame(list(md5s))
    md5s.to_csv(output_file, compression='gzip')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('nsrl_dir')
    parser.add_argument('output_file')
    args = parser.parse_args()
    filtering(args.nsrl_dir, args.output_file)
