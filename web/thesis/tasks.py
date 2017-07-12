from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django import db
from thesis.models import Report, DLL, UsesDLL


@shared_task
def create_uses_dll(link, dlls):
    dlls = map(lambda x: x.strip(), dlls.split(';'))
    dlls = filter(lambda x: x.endswith('.dll'), dlls)
    dlls = map(lambda x: x.replace('.dll', ''), dlls)
    r = Report.objects.get(link=link)
    for d in dlls:
        dll = DLL.objects.get(name=d)
        UsesDLL.objects.update_or_create(report=r, dll=dll)
        db.connection.close()
