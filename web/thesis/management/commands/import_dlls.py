from django.core.management.base import BaseCommand
from thesis.models import Report, DLL, UsesDLL
import pandas as pd
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

        for report in reports_frame.iterrows():
            r = Report.objects.get(link=report[0])
            dlls = map(lambda x: x.strip(), report[1].dlls.split(';'))
            dlls = filter(lambda x: x.endswith('.dll'), dlls)
            dlls = map(lambda x: x.replace('.dll', ''), dlls)
            for d in dlls:
                print(d)
                dll = DLL.objects.get(name=d)
                UsesDLL.objects.update_or_create(report=r, dll=dll)
