"""
    Calculate the functions that need to manually parse
    content that is over 10MB
"""
import re
import sys
import gzip
from os import walk


cut_dict = {
    'extract_peimphash': '<section id="static_analysis">',
    'extract_signatures': '<section id="signatures">',
    'extract_hosts': '<div class="tab-pane fade" id="network_hosts_tab">',
    'extract_domains': '<div class="tab-pane fade in active" id="network_domains_tab">',
    'extract_files': '<div class="tab-pane fade in active" id="summary_files">',
    'extract_keys': '<div class="tab-pane fade" id="summary_keys">',
    'extract_mutexes': '<div class="tab-pane fade" id="summary_mutexes">',
    'extract_peversioninfo': '<section id="static_analysis">',
    'extract_pesections': '<section id="static_analysis">',
    'extract_peresources': '<section id="static_analysis">',
    'extract_peimports': '<section id="static_analysis">',
    'extract_strings': '<section id="static_strings">',
    'extract_antivirus': '<section id="static_antivirus">',
    'extract_dynamic': '<script type="text/javascript">',
    'extract_http': '<div class="tab-pane fade" id="network_http_tab">',
    'extract_irc': '<div class="tab-pane fade" id="network_irc_tab">',
    'extract_smtp': '<div class="tab-pane fade" id="network_smtp_tab">',
    'extract_dropped': '<div class="tab-pane fade" id="dropped">',
}

def remove_whitespaces(content):
    """
        Removes whitespaces from content
    """
    re_replace = re.compile(r'>\s+<', re.MULTILINE)
    re_replace2 = re.compile(r'\s{3,}', re.MULTILINE)
    content = re.sub(re_replace, '><', content)
    content = re.sub(re_replace2, '', content)
    return content


def generate_func_cutpoints(content):
    """
        Generates list of pairs of function and where it should
        be on the content. Each position is based on the previous one
    """
    # Calculate the position
    key_pos = []
    for key, val in cut_dict.items():
        key_pos.append((key, content.find(val)))

    func_pos = sorted(key_pos, key=lambda x: x[1])
    size = len(func_pos)
    final_pos = []
    for idx, val in enumerate(func_pos[:0:-1]):
        final_pos.append((val[0], val[1] - func_pos[size - idx - 2][1]))
    final_pos.append((func_pos[0]))
    final_pos = final_pos[::-1]
    return final_pos


def main(data_dir):
    (_, _, reports) = next(walk(data_dir))
    data_dir = data_dir + '/' if data_dir[-1] != '/' else data_dir

    overflow_func = set()

    counter = 0
    for report in map(lambda x: data_dir + x, reports):
        with gzip.open(report) as gz_file:
            content = gz_file.read().decode('utf8')
        content = remove_whitespaces(content)

        # Over 10MB of text
        if len(content) > 10000000:
            func_cutpoints = generate_func_cutpoints(content)
            # Only relevant if offsets between relevant
            # info are over 10MB
            for idx, pair in enumerate(func_cutpoints[1:]):
                if pair[1] > 10000000:
                    # We enumerate from pos 1, idx is always one less than
                    # the real index, which is what we need
                    print((report, func_cutpoints[idx][0]))
                    overflow_func.add(func_cutpoints[idx][0])
        counter += 1
        if counter % 1000 == 0:
            print(overflow_func)
            overflow_func = set()
    print(overflow_func)



if __name__ == '__main__':
    main(sys.argv[1])
