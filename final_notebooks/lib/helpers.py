"""
    Some helper functions
"""

def mapKeywords(lst):
    """
        Takes a list and returns a function that takes
        an argument and returns true if it matches any item
        on the list
    """
    def apply_filter(x):
        for k in lst:
            if k in x.lower():
                return True
        return False
    return apply_filter


def normalize(val):
    import numpy as np
    """
        Normalizes the virustotal classification column, for unknown samples,
        -1 is returned
    """
    if val == 'n/a':
        return -1
    else:
        content = val.split('/')
        return np.round(int(content[0]) / int(content[1]), 2)
    
    
def calc_ratios(matrix):
    """
        Takes the output of a confusion matrix and calculates
        the FP and FN rate
    """
    import numpy as np
    fp_rate = matrix[0][1] / (matrix[0][1] + matrix[1][1])
    fn_rate = matrix[1][0] / (matrix[0][0] + matrix[1][0])
    cc_rate = (matrix[0][0] + matrix[1][1]) / np.sum(matrix)
    dr_rate = matrix[1][1] / (matrix[1][1] + matrix[1][0])
    return (fp_rate, fn_rate, cc_rate, dr_rate)


# Create the function that takes a pair of imports returns the NCD between them
# Based on https://arxiv.org/pdf/cs/0312044.pdf
# Using gzip for compression
import gzip
def NCD(a, b):
    concat = len(gzip.compress(a + b))
    print(concat)
    amin = min(len(gzip.compress(a)), len(gzip.compress(b)))
    amax = max(len(gzip.compress(a)), len(gzip.compress(b)))
    print(amin)
    print(amax)
    return (concat - amin) / amax


def train_test_split(samples, validation_size=0.1, balanced=True, malware_downscale=1):
    import pandas as pd
    
    goodware = samples[samples.malware == 0]
    malware = samples[samples.malware == 1]
    training_size = 1 - validation_size
    
    if balanced:
        # Limit the datasets by the smaller one
        lim = min(len(goodware), len(malware))
        
        g_train_len = m_train_len = int(lim * training_size)
        m_train_len = int(m_train_len * malware_downscale)
        g_val_len = m_val_len = int(lim * validation_size)
        m_val_len = int(m_val_len * malware_downscale)
    else:
        g_train_len = int(len(goodware) * training_size)
        m_train_len = int(len(malware) * training_size * malware_downscale)
        
        g_val_len = int(len(goodware) * validation_size)
        m_val_len = int(len(malware) * validation_size * malware_downscale)

    training = pd.concat([
        goodware[:g_train_len],
        malware[:m_train_len]
    ])
    validation = pd.concat([
        goodware[g_train_len:g_train_len + g_val_len],
        malware[m_train_len:m_train_len + m_val_len]
    ])
    
    return (training, validation)
        
