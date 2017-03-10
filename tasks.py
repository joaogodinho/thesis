from celery import Celery
import lib.data_loading as jcfg_data_loading


app = Celery('tasks', backend='rpc://')

@app.task
def extract_av_classification(submissions):
    import pandas as pd
    
    result = []
    for link in submissions:
        result.append([link, jcfg_data_loading.parse_av_classification(link)])
    return result
