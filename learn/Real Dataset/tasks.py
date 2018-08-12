import celery
import pickle
from sklearn.linear_model import LogisticRegression

app = celery.Celery('tasks', backend='rpc://', broker='pyamqp://jcfg:jcfg@localhost/thesis')
app.conf.accept_content = ['pickle', 'json']
print(app.conf.accept_content)

@app.task
def lr_train(x_train, y_train):
    return LogisticRegression(max_iter=1).fit(x_train, y_train)

@app.task
def lr_predict(lr, x_test):
    return picker.loads(lr).predict_proba(x_test)
