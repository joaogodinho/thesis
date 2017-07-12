from django.core.management.base import BaseCommand
from thesis.models import Report, DLL, UsesDLL
import pandas as pd
import gevent
from gevent import monkey; monkey.patch_all()
"""
    Imports used DLLs into the DB
"""


class Command(BaseCommand):
    help = 'Import CSV with DLLs into the DB'

    def create_uses_dll(self, report, dlls):
        r = Report.objects.get(link=report)
        for d in dlls:
            dll = DLL.objects.get(name=d)
            UsesDLL.objects.update_or_create(report=r, dll=dll)

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)
        parser.add_argument('dlls', type=str)

    def handle(self, *args, **options):
        file_name = options['file']
        dlls_name = options['dlls']
        with open(dlls_name, 'r') as file:
            dlls = list(map(lambda x: x.replace('.dll', ''), map(str.strip, file.readlines())))
        for dll in dlls:
            DLL.objects.create(name=dll)

        reports_frame = pd.read_csv(file_name)
        reports_frame = reports_frame.set_index('link')


        # Max number of sql connections
        BATCH_SIZE = 150
        reports = list(reports_frame.iterrows())
        batches = [reports[i:i+BATCH_SIZE] for i in range(0, len(reports), BATCH_SIZE)]
        for batch in batches:
            jobs = []
            for report in batch:
                dlls = map(lambda x: x.strip(), report[1].dlls.split(';'))
                dlls = filter(lambda x: x.endswith('.dll'), dlls)
                dlls = map(lambda x: x.replace('.dll', ''), dlls)
                jobs.append(gevent.spawn(self.create_uses_dll, report[0], dlls))
            print('Waiting for jobs...')
            gevent.joinall(jobs)
