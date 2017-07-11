from django.core.management.base import BaseCommand
from thesis.models import Report
import csv
import datetime
"""
    Imports reports headers' into the DB
"""


class Command(BaseCommand):
    help = 'Import CSV header file into DB'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        file_name = options['file']
        with open(file_name, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['file_type'].startswith('PE32 '):
                    Report.objects.create(
                        link=row['link'].split('/')[-2],
                        md5=row['md5'],
                        file_type=row['file_type'],
                        file_name=row['file_name'],
                        date=datetime.datetime.strptime(row['date'], '%d/%m/%Y').date())
