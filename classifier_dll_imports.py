# The following script generates a classifier for the static imports (dlls)
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score
import autosklearn.classification


data_folder = 'data/'
dlls_file = data_folder + 'dlls.csv.gz'
malware_file = data_folder + 'malware_samples.csv.gz'
goodware_file = data_folder + 'goodware_samples.csv.gz'

# Read into DataFrames
dlls = pd.read_csv(dlls_file)
dlls.set_index('link', inplace=True)
malware = pd.read_csv(malware_file)
malware.set_index('link', inplace=True)
malware['malware'] = 1
goodware = pd.read_csv(goodware_file)
goodware.set_index('link', inplace=True)
goodware['malware'] = 0


# Create the test and train sets (without temporal consistency)
upper_limit = len(goodware) if len(goodware) < len(malware) else len(malware)
# dataset = pd.concat([malware.sample(n=upper_limit), goodware.sample(n=upper_limit)])
dataset = pd.concat([malware[:upper_limit], goodware[:upper_limit]])
dataset = dataset.join(dlls)[['malware', 'dlls']]
dataset.dropna(inplace=True)
(train, test) = train_test_split(dataset)

# Create the count vectorizer
cv_token_pattern = u'[^;]+'
cv = CountVectorizer(token_pattern=cv_token_pattern)
# Generate the word vector
train_X = cv.fit_transform(train.dlls)
train_Y = train.malware
test_X = cv.transform(test.dlls)
test_Y = test.malware

# Fire autosklearn and pray
X_train = train_X
y_train = train_Y.values
X_test = test_X
y_test = test_Y.values

automl = autosklearn.classification.AutoSklearnClassifier(
    include_preprocessors=['no_preprocessing'],
    time_left_for_this_task=60*60*24*2,
    per_run_time_limit=60*5,
    ml_memory_limit=1024*8,
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
print("Accuracy score", sklearn.metrics.accuracy_score(y_test, predictions))