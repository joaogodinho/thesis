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
dataset = pd.concat([malware.sample(n=upper_limit), goodware.sample(n=upper_limit)])
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
automl = autosklearn.classification.AutoSklearnClassifier(
    time_left_for_this_task=60*60*24,
    per_run_time_limit=60*5,
    ml_memory_limit=1024*8,
    delete_tmp_folder_after_terminate=False,
    delete_output_folder_after_terminate=False)
automl.fit(train_X, train_Y)

predictions = automl.predict(test_X)
print('Accuracy score', accuracy_score(test_Y, predictions))