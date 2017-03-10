import pandas as pd


# Load the Headers CSV file into a Pandas dataframe
# and set the date column as the index
def loadHeadersCSV(filename):
    # Read CSV into a pandas dataframe
    df = pd.read_csv(filename)
    # Convert from string to date
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
    # Convert file type to string
    df['file_type'] = df['file_type'].astype(str)
    # Set date as index
    df = df.set_index('date')
    return df


# Takes a CSV file with links and a data dir
# and returns a list with the missing links in the dir
def check_link(submissions, data_dir='data/analyses_gz'):
    from os import walk
    
    files = []
    for dirpath, dirname, filenames in walk(data_dir):
        files.extend(filenames)
        break
        
    missing = []
    for s in submissions:
        if s not in files:
            missing.append(s)
    return missing


# Parses the static imports from raw html
# submission given on input
# Returns a list with unique imports
def parse_static_imports(submission, data_dir='data/analyses_gz'):
    from lxml import etree
    import gzip
    # Spend as little time as possible with the file open
    with gzip.open(data_dir + '/' + submission, 'rb') as gz_file:
        content = gz_file.read()
    doc = etree.HTML(content)
    imports = set()
    for x in doc.xpath('//div[@id="pe_imports"]//a/text()'):
        # Some have 'None' on the imports, weird but need to be removed
        if x != 'None':
            # Ignore unicode/ansi names
            if x[-1] == 'W' or x[-1] == 'A':
                imports.add(x[:-1].lower().strip())
            else:
                imports.add(x.lower().strip())
    return list(imports)


# Parses the malware classification from raw html
# submission given on input
# Returns dict with vendors and their classification
def parse_av_classification(submission, data_dir='data/analyses_gz'):
    from lxml import etree
    import gzip
    # Spend as little time as possible with the file open
    with gzip.open(data_dir + '/' + submission, 'rb') as gz_file:
        content = gz_file.read()
    doc = etree.HTML(content)
    classification = dict()
    # [1:] to skip th
    for x in doc.xpath('//section[@id="static_antivirus"]//table/tr')[1:]:
        classification[x[0].xpath('text()')[0].lower()] = x[1].xpath('span/text()')[0].lower()
    return classification
