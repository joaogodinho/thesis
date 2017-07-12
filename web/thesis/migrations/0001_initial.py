# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-10 11:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DLL',
            fields=[
                ('name', models.CharField(db_index=True, editable=False, max_length=50, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='DLLFunction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, editable=False, max_length=100)),
                ('dll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='thesis.DLL')),
            ],
        ),
        migrations.CreateModel(
            name='FunctionImport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('func_import', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='thesis.DLLFunction')),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('link', models.CharField(db_index=True, editable=False, max_length=43, primary_key=True, serialize=False)),
                ('md5', models.CharField(db_index=True, editable=False, max_length=32)),
                ('file_type', models.CharField(editable=False, max_length=255)),
                ('file_name', models.CharField(editable=False, max_length=255)),
                ('date', models.DateField(editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='UsesDLL',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='thesis.DLL')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='thesis.Report')),
            ],
        ),
        migrations.AddField(
            model_name='functionimport',
            name='report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='thesis.Report'),
        ),
        migrations.AlterUniqueTogether(
            name='usesdll',
            unique_together=set([('dll', 'report')]),
        ),
        migrations.AlterUniqueTogether(
            name='functionimport',
            unique_together=set([('report', 'func_import')]),
        ),
        migrations.AlterUniqueTogether(
            name='dllfunction',
            unique_together=set([('name', 'dll')]),
        ),
    ]