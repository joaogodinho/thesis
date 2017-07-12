from django.core.management.base import BaseCommand
from thesis.models import Report, DLL, UsesDLL
from thesis.tasks import create_uses_dll
import pandas as pd
from celery import group
"""
    Imports used DLLs into the DB
"""


class Command(BaseCommand):
    help = 'Import CSV with DLLs into the DB'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)
        parser.add_argument('dlls', type=str)

    def handle(self, *args, **options):
        file_name = options['file']
        dlls_name = options['dlls']
        # with open(dlls_name, 'r') as file:
        #     dlls = list(map(lambda x: x.replace('.dll', ''), map(str.strip, file.readlines())))
        # for dll in dlls:
        #     DLL.objects.create(name=dll)

        reports_frame = pd.read_csv(file_name)
        reports_frame = reports_frame.set_index('link')

        # Max number of sql connections
        BATCH_SIZE = 150
        reports = list(reports_frame.iterrows())
        batches = [reports[i:i+BATCH_SIZE] for i in range(0, len(reports), BATCH_SIZE)]
        for batch in batches:
            jobs = group([create_uses_dll.s(report[0], report[1].tolist()[0]) for report in batch])
            print('Waiting for jobs...')
            result = jobs.apply_async()
            print('Done.')
