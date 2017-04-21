from celery import Celery
import pandas as pd
import numpy as np
import lib.data_loading as jcfg_data_loading
import lib.helpers as jcfg_helpers


app = Celery('tasks', backend='rpc://')


@app.task
def extract_av_classification(submission, data_dir='data/analyses_gz'):
    """
        Takes the submission ID and returns a dictionary
        with each Antivirus and its classification
    """
    import gzip
    from lxml import etree

    with gzip.open(data_dir + '/' + submission, 'rb') as gz_file:
            content = gz_file.read()

    doc = etree.HTML(content)
    classification = dict()
    # [1:] to skip th
    for x in doc.xpath('//section[@id="static_antivirus"]//table/tr')[1:]:
        classification[x[0].xpath('text()')[0].lower()] = x[1].xpath('span/text()')[0].lower()
    return classification


@app.task
def extract_imports(submission, data_dir='data/analyses_gz'):
    """
        Takes the submission ID and returns a string with
        the imports separated by a semicolon
    """
    from lxml import etree
    import gzip
    
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
    return ';'.join(imports)


#################################################


@app.task
def extract_av_classification2(submissions):
    result = []
    for link in submissions:
        result.append([link, jcfg_data_loading.parse_av_classification(link)])

    result = np.array(result)
    return pd.DataFrame(data=list(result[:,1]), index=result[:,0]).to_json()


@app.task
def extract_imports2(submissions):
    result = []
    for link in submissions:
        result.append([link, ';'.join(jcfg_data_loading.parse_static_imports(link))])

    result = np.array(result, dtype=str)
    return pd.DataFrame(data=dict([('imports', result[:,1])]), index=result[:,0]).to_json()


@app.task
def join_dataframes(df_list):
    return pd.concat([pd.read_json(json) for json in df_list]).to_json()


@app.task
def count_fn_rate(fn_count, json_samples, threshold=0.5):
    tp_count = fn_count.copy()
    samples = pd.read_json(json_samples, orient='records').drop(['md5', 'link'], axis=1)
    for _, sample in samples.iterrows():
        vendors = sample.dropna().keys().tolist()
        vendors_count = len(vendors)

        # Check if "malware" by looking at the majority of classifcations
        vendors_clean = sample[sample == 'clean']
        if vendors_clean.count() / vendors_count < threshold:
            for vendor in vendors:
                tp_count[vendor] += 1
            for vendor in vendors_clean.keys():
                fn_count[vendor] += 1
        
    return fn_count, tp_count 


@app.task
def count_fp_rate(fp_count, json_samples, threshold=0.5):
    tn_count = fp_count.copy()
    samples = pd.read_json(json_samples, orient='records').drop(['md5', 'link'], axis=1)
    for _, sample in samples.iterrows():
        vendors = sample.dropna().keys().tolist()
        vendors_count = len(vendors)

        # Check if "not malware" by looking at the majority of classifcations
        vendors_not_clean = sample.dropna()[sample != 'clean']
        if vendors_not_clean.count() / vendors_count < threshold:
            for vendor in vendors:
                tn_count[vendor] += 1
            for vendor in vendors_not_clean.keys():
                fp_count[vendor] += 1
        
    return fp_count, tn_count 


@app.task
def count_fp_rate2(fp_count, baseline_vendors, json_samples, threshold=0.5):
    tn_count = fp_count.copy()
    samples = pd.read_json(json_samples, orient='records').drop(['md5', 'link'], axis=1)
    for _, sample in samples.iterrows():
        sample_filtered = sample[baseline_vendors].dropna()
        baseline_clean = sample_filtered[sample_filtered == 'clean']
        
        # Check if "not malware" by looking at the majority of classifcations in the baseline
        if baseline_clean.count() / sample_filtered.count() > threshold:
            vendors = sample[list(fp_count.keys())].dropna()
            tn_vendors = vendors.keys().tolist()
            for vendor in vendors.keys():
                tn_count[vendor] += 1
            
            vendors_fp = vendors[vendors != 'clean']
            for vendor in vendors_fp.keys():
                fp_count[vendor] += 1
        
    return fp_count, tn_count


@app.task
def simple_heuristic(common_features, malware_features, goodware_features, samples):
    common_features = set(common_features)
    malware_features = set(malware_features)
    goodware_features = set(goodware_features)
    
    relevant_features = set.union(common_features, malware_features, goodware_features)
    common_count = 0
    unknown_count = 0
    fp_count = 0
    tp_count = 0
    fn_count = 0
    tn_count = 0

    for _, sample in pd.read_json(samples, orient='records').iterrows():
        features = set(sample.imports.split(';'))
        # Exclude imports I've never seen
        features = features.intersection(relevant_features)

        # Common only features
        common = features.difference(common_features)
        if len(common) == 0:
            common_count += 1
            continue

        # Malware only features
        diff = common.difference(malware_features)
        if len(diff) == 0:
            # True positive
            if sample.malware == 1:
                tp_count += 1
            # False positive
            else:
                fp_count += 1
            continue

        # Goodware only features
        diff = common.difference(goodware_features)
        if len(diff) == 0:
            # True negative
            if sample.malware == 0:
                tn_count += 1
            else:
                fn_count += 1
            continue
        
        # No if matched, means only unknown features
        unknown_count += 1
    return {'common_count': common_count,
            'fp_count': fp_count,
            'tp_count': tp_count,
            'fn_count': fn_count,
            'tn_count': tn_count,
            'unknown_count': unknown_count}


@app.task
def multiple_ndc(pairs):
    result = []
    for pair in pairs:
        result.append(jcfg_helpers.NDC(pair[0], pair[1]))
    return result

