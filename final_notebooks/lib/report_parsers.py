import json
from lxml import etree
import re
"""
    Contains all the functions to extract the reports' info
"""

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


def extract_peimphash(doc):
    """
        Returns the PE imphash or empty
    """
    imphash = list(map(lambda x: x.strip(), doc.xpath('//section[@id="static_analysis"]/div/div[@class="well"]/text()')))
    return imphash[0] if imphash else None


def extract_signatures(doc):
    """
        Returns the matched signatures or empty
    """
    # Lambda to remove the #
    sigs = list(map(lambda x: x[1:], doc.xpath('//section[@id="signatures"]/a/@href')))
    return sigs if sigs else None


def extract_hosts(doc):
    """
        Returns the hosts or empty
    """
    # Lambda to remove whitespaces
    return list(map(lambda x: x.strip(), doc.xpath('//div[@id="network_hosts_tab"]/section[@id="hosts"]/table/tr/td/text()'))) or None


def extract_domains(doc):
    """
        Returns the domains + host dict or empty
    """
    # Cannot use zip since some domains have no matching host
    domains = dict()
    for row in doc.xpath('//div[@id="network_domains_tab"]/section[@id="domains"]/table/tr[position()>1]'):
        host = row.xpath('td[2]/text()')
        domain = row.xpath('td[1]/text()')
        if not domain:
            continue
        if not host:
            host = ''
        else:
            host = host[0]
        domains[domain[0]] = host
    return domains or None


def extract_files(doc):
    """
        Returns the touched files or empty
    """
    # Lambda to remove whitespaces, filter to remove empty values
    return list(filter(None, map(lambda x: x.strip(), doc.xpath('//div[@id="summary_files"]/div/text()')))) or None


def extract_keys(doc):
    """
        Returns the touched registry keys or empty
    """
    # Lambda to remove whitespaces, filter to remove empty values
    return list(filter(None, map(lambda x: x.strip(), doc.xpath('//div[@id="summary_keys"]/div/text()')))) or None


def extract_mutexes(doc):
    """
        Returns the mutexes or empty
    """
    # Lambda to remove whitespaces, filter to remove empty values
    return list(filter(None, map(lambda x: x.strip(), doc.xpath('//div[@id="summary_mutexes"]/div/text()')))) or None


def extract_peversioninfo(doc):
    """
        Returns PE version info as a dict or empty
    """
    info = dict()
    for tr in doc.xpath('//section[@id="static_analysis"]//div[@id="pe_versioninfo"]/table/tr'):
        key = tr.xpath('th/text()')
        val = tr.xpath('td/span/text()')
        # Skip rows without value or heaader
        if not val or not key:
            continue
        info[key[0]] = val[0]
    return info or None


def extract_pesections(doc):
    """
        Returns PE sections as a dict or empty
    """
    sections = []
    # Use the table header as keys
    headers = list(map(lambda x: x.lower(),
                  doc.xpath('//section[@id="static_analysis"]//div[@id="pe_sections"]/table/tr[1]/th/text()')))
    for tr in doc.xpath('//section[@id="static_analysis"]//div[@id="pe_sections"]/table/tr[position()>1]'):
        sections.append(dict(zip(headers, tr.xpath('td/text()'))))
    return sections or None


def extract_peresources(doc):
    """
        Returns PE resources as a dict or empty
    """
    sections = []
    headers = list(map(lambda x: x.lower(),
                  doc.xpath('//section[@id="static_analysis"]//div[@id="pe_resources"]/table/tr[1]/th/text()')))
    for tr in doc.xpath('//section[@id="static_analysis"]//div[@id="pe_resources"]/table/tr[position()>1]'):
        sections.append(dict(zip(headers, tr.xpath('td/text()'))))
    return sections or None


def extract_peimports(doc):
    """
        Returns PE imports as a dict or empty
    """
    imports = dict()
    # Imports from each dll are inside a div
    for well in doc.xpath('//section[@id="static_analysis"]//div[@id="pe_imports"]/div[@class="well"]'):
        dll = well.xpath('div[1]/strong/text()')[0].lower().replace('library ', '')
        functions = well.xpath('div[position()>1]/span/a/text()')
        imports[dll] = functions
    return imports or None


def extract_strings(doc):
    """
        Returns strings or empty
    """
    return doc.xpath('//section[@id="static_strings"]/div[@class="well"]/div/text()') or None


def extract_antivirus(doc):
    """
        Returns the antivirus as a dict or empty
    """
    av = doc.xpath('//section[@id="static_antivirus"]/table/tr[position()>1]/td[1]/text()')
    clss = doc.xpath('//section[@id="static_antivirus"]/table/tr[position()>1]/td[2]/span/text()')
    return dict(zip(av, clss)) or None


def extract_dynamic(doc):
    """
        Returns the dynamic calls as a dict or empty
        Must use the source HTML due to maximum number of chars
        text() returns (10000000). Some dynamic traces are bigger
    """
    data = doc.xpath('//script[@type="text/javascript" and contains(., "graph_raw_data")]/text()')
    # If there's no match
    if not data:
        return None

    # Get the json data only, removing beginning var def and ; ending
    data = data[0].strip().replace('var graph_raw_data = ', '').strip()[:-1]
    return json.loads(data)


def extract_http(doc):
    """
        Returns the HTTP requests as dict or empty
    """
    http = []
    for row in doc.xpath('//div[@id="network_http_tab"]/table/tr[position()>1]'):
        http.append({row.xpath('td[1]/text()')[0]: row.xpath('td[2]/pre/text()')[0]})
    return http or None


def extract_irc(doc):
    """
        Returns the IRC traffic or empty
    """
    return list(map(lambda x: x.strip(), doc.xpath('//div[@id="network_irc_tab"]/pre/text()'))) or None


def extract_smtp(doc):
    """
        Returns pair with number of SMTP requests and example or empty
    """
    example = doc.xpath('//div[@id="network_smtp_tab"]/pre/text()')
    if example:
        example = example[0].strip()
        number = doc.xpath('//div[@id="network_smtp_tab"]/p/text()')[0].split(': ')[1]
        return (number, example)
    return None


def extract_dropped(doc):
    """
        Returns list of dropped files or empty
    """
    files = []
    for drop in doc.xpath('//div[@id="dropped"]//table'):
        keys = map(lambda x: x.lower(), drop.xpath('tr/th/text()'))
        values = map(lambda x: x.strip(), drop.xpath('tr/td/text()|tr/td/b/text()'))
        files.append(dict(zip(keys, values)))
    return files or None


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
        pos = content.find(val)
        if pos == -1:
            continue
        key_pos.append((key, pos))

    func_pos = sorted(key_pos, key=lambda x: x[1])
    size = len(func_pos)
    final_pos = []
    for idx, val in enumerate(func_pos[:0:-1]):
        final_pos.append((val[0], val[1] - func_pos[size - idx - 2][1]))
    final_pos.append((func_pos[0]))
    final_pos = final_pos[::-1]
    return final_pos


def extract_dynamic_huge(content):
    """
        Parses dynamic input > 10MB with regexes
    """
    start_str = 'var graph_raw_data = '
    stop_str = '</script>'
    start_idx = content.find(start_str)
    content = content[len(start_str) + start_idx:].strip()
    stop_idx = content.find(stop_str)
    content = content[:stop_idx].strip()[:-1]
    return json.loads(content)


# Keep RE compiled
re_strings = re.compile(r'<div>([^<]+)<\/div>')
re_files = re.compile(r'([^<]+)<br \/>')
re_keys = re.compile(r'([^<]+)<br \/>')
re_mutexes = re.compile(r'([^<]+)<br \/>')


def extract_strings_huge(content):
    """
        Parses strings > 10MB with regexes
    """
    return re.findall(re_strings, content)


def extract_files_huge(content):
    """
        Parses files > 10MB with regexes
    """
    start_str = '<div class="well mono">'
    stop_str = '<div class="tab-pane fade" id="summary_keys">'
    start_idx = content.find(start_str)
    stop_idx = content.find(stop_str)
    content = content[len(start_str) + start_idx:stop_idx]
    return re.findall(re_files, content)


def extract_keys_huge(content):
    """
        Parses keys > 10MB with regexes
    """
    start_str = '<div class="well mono">'
    stop_str = '<div class="tab-pane fade" id="summary_mutexes">'
    start_idx = content.find(start_str)
    stop_idx = content.find(stop_str)
    content = content[len(start_str) + start_idx:stop_idx]
    return re.findall(re_keys, content)


def extract_mutexes_huge(content):
    """
        Parses mutexes > 10MB with regexes
    """
    start_str = '<div class="well mono">'
    stop_str = '</section>'
    start_idx = content.find(start_str)
    stop_idx = content.find(stop_str)
    content = content[len(start_str) + start_idx:stop_idx]
    return re.findall(re_mutexes, content)
