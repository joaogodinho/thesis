from django.contrib import admin
from .models import Report, DLL, UsesDLL


class ReportAdmin(admin.ModelAdmin):
    list_display = ('link', 'md5', 'file_type', 'date')
    search_fields = ['link', 'md5']


class DLLAdmin(admin.ModelAdmin):
    list_display = ('name',)


class UsesDLLAdmin(admin.ModelAdmin):
    list_display = ('report', 'dll')


admin.site.register(Report, ReportAdmin)
admin.site.register(DLL, DLLAdmin)
admin.site.register(UsesDLL, UsesDLLAdmin)
