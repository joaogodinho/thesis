import pandas as pd
import numpy as np
import math
import re
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import StratifiedKFold
from sklearn.utils import shuffle
from sklearn.decomposition import PCA
from scipy import interp
from sklearn.pipeline import Pipeline
from sklearn.externals import joblib

data_folder = '~/security_privacy2018/data/'
dataset1_file = data_folder + 'dataset1.csv.gz'
dlls_imports_file = data_folder + 'dlls.csv.gz'
dlls_invalid_file = data_folder + 'dlls_invalid.csv.gz'

imports1_file = data_folder + 'dataset1_imports.csv.gz'

cv_token_pattern = u'[^;]+'
# Remove imports' extension
def token_preprocessor(s):
    return ''.join(re.split('\..{0,3}', s))

imports = pd.read_csv(dlls_imports_file)
imports = imports.set_index('link')

# Load dataset
dataset = pd.read_csv(dataset1_file)
dataset = dataset.set_index('link')
dataset = dataset.join(imports, how='inner')
dataset.dropna(inplace=True)
#dataset.drop_duplicates(subset='md5', keep='last', inplace=True)
dataset = shuffle(dataset)

dlls_invalid = list(pd.read_csv(dlls_invalid_file)['0'].values)
# display(dlls_invalid)

cv = CountVectorizer(token_pattern=cv_token_pattern, stop_words=dlls_invalid, lowercase=False)
                     #preprocessor=token_preprocessor, lowercase=False)
cv.fit(dataset.dlls)

classifier = LogisticRegression(C=1, verbose=5)

classifier.fit(cv.transform(dataset.dlls), dataset.malware)


pipe = Pipeline(steps=[('cv', cv), ('logistic', classifier)])

pipe.fit(dataset.dlls, dataset.malware)

joblib.dump(pipe, 'lr_1.pk1', compress=9, protocol=2)