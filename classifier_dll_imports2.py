# The following script generates a classifier for the static imports (dlls)
import autosklearn.classification
from IPython.display import display
import pandas as pd
import numpy as np
import math
import re
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn import svm
from sklearn.metrics import roc_curve, auc, accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import train_test_split
from scipy import interp

data_folder = 'data/'
final_dataset_file = data_folder + 'dataset_v2.csv.gz'
selected_imports_file = data_folder + 'selected_imports.csv.gz'

cv_token_pattern = u'[^;]+'
vec_stop_words = ['*invalid*']
# Remove imports' extension
def token_preprocessor(s):
    return re.split('\..{0,3}', s)[0]

# Load dataset
dataset = pd.read_csv(final_dataset_file)
dataset = dataset.set_index('link')

# Load the selected features
features = pd.read_csv(selected_imports_file)
features = features['0'].values

cv = CountVectorizer(token_pattern=cv_token_pattern, stop_words=vec_stop_words,
                     preprocessor=token_preprocessor, vocabulary=features)
cv.fit(dataset.dlls)

X_train, X_test, y_train, y_test = train_test_split(cv.transform(dataset.dlls), dataset.malware)

# Fire autosklearn and pray
automl = autosklearn.classification.AutoSklearnClassifier(
    include_preprocessors=['no_preprocessing'],
    time_left_for_this_task=60*60*24*2,
    # time_left_for_this_task=60*5,
    per_run_time_limit=60*10,
    # per_run_time_limit=60,
    ml_memory_limit=1024*6,
    # ml_memory_limit=2028,
    tmp_folder='/tmp/autoslearn_cv_example_tmp',
    output_folder='/tmp/autosklearn_cv_example_out',
    delete_tmp_folder_after_terminate=False,
    delete_output_folder_after_terminate=False,
    resampling_strategy='cv',
    resampling_strategy_arguments={'folds': 10},
    ensemble_size=1,
    initial_configurations_via_metalearning=0)

# fit() changes the data in place, but refit needs the original data. We
# therefore copy the data. In practice, one should reload the data
automl.fit(X_train.copy(), y_train.copy(), dataset_name='malwr', metric=autosklearn.metrics.roc_auc)
# During fit(), models are fit on individual cross-validation folds. To use
# all available data, we call refit() which trains all models in the
# final ensemble on the whole dataset.
automl.refit(X_train.copy(), y_train.copy())

print(automl.show_models())
predictions = automl.predict(X_test)
print("Accuracy score", accuracy_score(y_test, predictions))
print("ROC", roc_curve(y_test, predictions))
