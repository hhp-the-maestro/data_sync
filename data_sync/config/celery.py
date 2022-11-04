from __future__ import absolute_import
from celery import Celery
import json
from db_utils import DBUtils
import os

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", None)

if CELERY_BROKER_URL:
    app = Celery('config', backend="rpc://", broker=CELERY_BROKER_URL)
else:
    app = Celery('config', backend="rpc://")


app.autodiscover_tasks()


@app.task
def populate_db(filename):
    utils = DBUtils()
    file = open(filename)
    data  = json.load(file)
    for table in data:
        for row in data[table]:
            async_insert_in_table.apply_async((table, row))

    return 1

@app.task
def async_insert_in_table(table, row):
    DBUtils().insert_in_table(table, row)
    return 1

@app.task
def async_update_in_db(table, filters, data):
    DBUtils().update_by_column(table, filters, data)
    return 1