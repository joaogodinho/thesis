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