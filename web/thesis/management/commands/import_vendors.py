from django.core.management.base import BaseCommand
from thesis.models import Report, DLL, UsesDLL
import pandas as pd
"""
    Imports vendors into the DB
"""


class Command(BaseCommand):
    help = 'Import CSV with vendors into the DB'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        file_name = options['file']

        reports_frame = pd.read_csv(file_name)
        reports_frame = reports_frame.set_index('link')

        for report in reports_frame.iterrows():
            r = Report.objects.get(link=report[0])
            dlls = map(lambda x: x.strip(), report[1].dlls.split(';'))
            dlls = filter(lambda x: x.endswith('.dll'), dlls)
            dlls = map(lambda x: x.replace('.dll', ''), dlls)
            for d in dlls:
                dll = DLL.objects.get(name=d)
                UsesDLL.objects.update_or_create(report=r, dll=dll)
