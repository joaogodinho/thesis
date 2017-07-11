from django.db import models


class Report(models.Model):
    """
        Skeleton for report, contains basic information
        about a report
    """

    link = models.fields.CharField(max_length=43, primary_key=True, editable=False, db_index=True)
    md5 = models.fields.CharField(max_length=32, editable=False, db_index=True)
    file_type = models.fields.CharField(max_length=255, editable=False)
    file_name = models.fields.CharField(max_length=255, editable=False)
    date = models.fields.DateField(editable=False)

    def __str__(self):
        return '{}'.format(self.link)


class DLL(models.Model):
    """
        Represents the used DLLs
    """

    name = models.fields.CharField(max_length=50, primary_key=True, editable=False, db_index=True)

    def __str__(self):
        return '{}'.format(self.name)


class UsesDLL(models.Model):
    """
        Connects the Report with a given DLL
    """

    report = models.ForeignKey('Report', on_delete=models.CASCADE)
    dll = models.ForeignKey('DLL', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('dll', 'report',)

    def __str__(self):
        return '{} - {}'.format(self.report, self.dll)


class DLLFunction(models.Model):
    """
        Represents a DLL function
    """

    name = models.CharField(max_length=100, editable=False, db_index=True)
    dll = models.ForeignKey('DLL', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'dll',)

    def __str__(self):
        return '{}: {}'.format(self.dll, self.name)


class FunctionImport(models.Model):
    """
        Represents an import by some report
    """

    report = models.ForeignKey('Report', on_delete=models.CASCADE)
    func_import = models.ForeignKey('DLLFunction', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('report', 'func_import',)

    def __str__(self):
        return '{} - {}'.format(func_import, report)
